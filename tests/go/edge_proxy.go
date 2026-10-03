//go:build go1.26

// Package edgeproxy forwards partner traffic to the internal billing API and
// seals the partner token it attaches upstream.
package edgeproxy

import (
	"crypto/rand"
	"crypto/rsa"
	"errors"
	"fmt"
	"net/http"
	"net/http/httputil"
	"net/url"
)

// ErrUpstream marks failures reported by the billing API.
type ErrUpstream struct {
	Status int
}

func (e *ErrUpstream) Error() string {
	return fmt.Sprintf("upstream status %d", e.Status)
}

// NewProxy returns a reverse proxy that tags every request with the partner ID.
func NewProxy(target *url.URL, partnerID string) *httputil.ReverseProxy {
	proxy := httputil.NewSingleHostReverseProxy(target)
	base := proxy.Director
	proxy.Director = func(r *http.Request) {
		base(r)
		r.Header.Set("X-Partner-ID", partnerID)
	}
	return proxy
}

// SealToken encrypts the partner token for the upstream key holder.
func SealToken(pub *rsa.PublicKey, token []byte) ([]byte, error) {
	sealed, err := rsa.EncryptPKCS1v15(rand.Reader, pub, token)
	if err != nil {
		return nil, fmt.Errorf("seal partner token: %w", err)
	}
	return sealed, nil
}

// UpstreamStatus extracts the billing API status from an error chain.
func UpstreamStatus(err error) (int, bool) {
	var upstream *ErrUpstream
	if errors.As(err, &upstream) {
		return upstream.Status, true
	}
	return 0, false
}

// PartnerID returns the partner identifier the edge gateway attached.
func PartnerID(r *http.Request) string {
	id := r.Header.Get("X-Partner-ID")
	if id == "" {
		panic("edgeproxy: request has no X-Partner-ID header")
	}
	return id
}
