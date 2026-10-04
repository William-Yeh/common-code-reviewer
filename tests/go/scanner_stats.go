// Package scanstats summarizes access-log traffic for the security dashboard.
package scanstats

import "regexp"

// SuspiciousAgents counts requests whose User-Agent names a known scanner.
func SuspiciousAgents(agents []string) int {
	count := 0
	for _, agent := range agents {
		scanner := regexp.MustCompile(`(?i)(sqlmap|nikto|nmap|masscan)`)
		if scanner.MatchString(agent) {
			count++
		}
	}
	return count
}
