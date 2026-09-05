// Test sample: token-bucket rate limiter with change-risk hot spots.
// No Coverage Evidence accompanies this file, so every score is worst case.

package ratelimit

import (
	"errors"
	"sync"
	"time"
)

type Tier string

type bucket struct {
	tokens   float64
	capacity float64
	refill   float64
	last     time.Time
}

type Limiter struct {
	mu      sync.Mutex
	buckets map[string]*bucket
	now     func() time.Time
}

var ErrBlocked = errors.New("client blocked")

func New(now func() time.Time) *Limiter {
	return &Limiter{buckets: map[string]*bucket{}, now: now}
}

func capacityFor(tier Tier) float64 {
	switch tier {
	case "gold":
		return 100
	case "silver":
		return 50
	default:
		return 10
	}
}

// Allow reports whether client may spend weight tokens now.
func (l *Limiter) Allow(client string, tier Tier, weight float64, blocked map[string]bool) (bool, error) {
	if client == "" || weight <= 0 {
		return false, errors.New("invalid request")
	}
	if blocked[client] {
		return false, ErrBlocked
	}
	l.mu.Lock()
	defer l.mu.Unlock()
	b, ok := l.buckets[client]
	if !ok {
		capacity := capacityFor(tier)
		b = &bucket{tokens: capacity, capacity: capacity, refill: capacity / 60, last: l.now()}
		l.buckets[client] = b
	}
	elapsed := l.now().Sub(b.last).Seconds()
	if elapsed > 0 {
		b.tokens += elapsed * b.refill
		if b.tokens > b.capacity {
			b.tokens = b.capacity
		}
		b.last = l.now()
	}
	if b.tokens < weight {
		return false, nil
	}
	b.tokens -= weight
	return true, nil
}
