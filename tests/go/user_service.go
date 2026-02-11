// Test sample #2: User service — targets general SKILL.md principles
// Focuses on: OCP, ISP, Testability, Clean Code, Architecture, FP, Security

package service

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"os/exec"
	"time"
)

// ─── ISP: Fat interface ─────────────────────────────────────────────
// [ISSUE: ISP violation — 8 methods, most implementations only need a subset]
type UserStore interface {
	FindByID(id string) (map[string]interface{}, error)
	FindByEmail(email string) (map[string]interface{}, error)
	Save(user map[string]interface{}) error
	Delete(id string) error
	BulkImport(users []map[string]interface{}) (int, error)
	ExportCSV(w io.Writer) error
	GenerateReport() ([]byte, error)
	ArchiveInactive(days int) (int, error)
}

// ─── OCP: Switch on action type ─────────────────────────────────────
// [ISSUE: OCP violation — every new action requires modifying this function]
func HandleUserAction(action string, userID string, payload map[string]interface{}) error {
	switch action {
	case "activate":
		fmt.Println("Activating user:", userID)
		return nil
	case "deactivate":
		fmt.Println("Deactivating user:", userID)
		return nil
	case "suspend":
		fmt.Println("Suspending user:", userID)
		return nil
	case "reset_password":
		fmt.Println("Resetting password for:", userID)
		return nil
	case "promote":
		fmt.Println("Promoting user:", userID)
		return nil
	// [ISSUE: No default — unknown actions silently succeed (return nil)]
	}
	return nil
}

// ─── Architecture: Layer violation + anemic domain ──────────────────
// [ISSUE: Anemic domain — struct is a pure data bag, no behavior]
type User struct {
	ID        string
	Name      string
	Email     string
	Role      string // [ISSUE: string instead of a defined type]
	Status    string // [ISSUE: string instead of a defined type]
	CreatedAt time.Time
	LastLogin time.Time
}

// ─── FP: Hidden side effects ────────────────────────────────────────
// [ISSUE: Named "Count" but has side effects — writes file and sends HTTP]
func CountActiveUsers(users []User) int {
	count := 0
	for _, u := range users {
		if u.Status == "active" {
			count++
		}
	}

	// [ISSUE: Hidden side effect in a counting function]
	data, _ := json.Marshal(map[string]int{"active_count": count})
	os.WriteFile("/tmp/user-stats.json", data, 0644)
	http.Post("https://analytics.internal/track", "application/json",
		bytes.NewReader(data))

	return count
}

// ─── Testability ────────────────────────────────────────────────────
type UserService struct {
	// [ISSUE: No exported fields or constructor injection — uses global/hardcoded deps]
}

// [ISSUE: Non-deterministic — uses time.Now() directly]
func (s *UserService) IsInactive(user User, thresholdDays int) bool {
	return time.Since(user.LastLogin).Hours()/24 > float64(thresholdDays)
}

// [ISSUE: Hard-coded filesystem dependency — untestable]
func (s *UserService) LoadConfig() (map[string]string, error) {
	data, err := os.ReadFile("/etc/app/users.json")
	if err != nil {
		return nil, err
	}
	var config map[string]string
	json.Unmarshal(data, &config) // [ISSUE: Unmarshal error ignored]
	return config, nil
}

// ─── Clean Code ─────────────────────────────────────────────────────

// [ISSUE: Deep nesting — 4 levels]
func (s *UserService) DeactivateInactive(users []User, days int) []User {
	var result []User
	for _, u := range users {
		if u.LastLogin.IsZero() == false {
			if time.Since(u.LastLogin).Hours()/24 > float64(days) {
				if u.Role != "admin" {
					if u.Status != "protected" {
						u.Status = "inactive"
						result = append(result, u)
					}
				}
			}
		}
	}
	return result
}

// [ISSUE: Mixed abstraction levels — config, business logic, file I/O, HTTP all in one]
func (s *UserService) GenerateReport(users []User) (string, error) {
	config, _ := s.LoadConfig() // [ISSUE: Error ignored]
	reportDir := config["report_dir"]

	// [ISSUE: Code duplication — same role-counting logic could be shared]
	adminCount := 0
	editorCount := 0
	for _, u := range users {
		if u.Role == "admin" {
			adminCount++
		} else if u.Role == "editor" {
			editorCount++
		}
	}

	report := fmt.Sprintf("Admins: %d, Editors: %d", adminCount, editorCount)

	// [ISSUE: Side effect in report generation]
	os.WriteFile(fmt.Sprintf("%s/report_%s.txt", reportDir, time.Now().Format("20060102")),
		[]byte(report), 0644)

	return report, nil
}

// [ISSUE: Bad naming — what does "proc" do? What are "d", "f", "r"?]
func proc(d []map[string]interface{}, f string) []map[string]interface{} {
	var r []map[string]interface{}
	for _, x := range d {
		// [ISSUE: Duplicated email validation]
		if e, ok := x["email"].(string); ok && e != "" {
			r = append(r, x)
		}
	}
	return r
}

// [ISSUE: Dead code — never called]
func oldNotify(email string, msg string) {
	fmt.Printf("Sending to %s: %s\n", email, msg)
}

// ─── Security ───────────────────────────────────────────────────────
// [ISSUE: Command injection — unsanitized username passed to shell command]
func ExportUserData(username string, format string) (string, error) {
	out, err := exec.Command("sh", "-c",
		fmt.Sprintf("user-export --user %s --format %s", username, format)).Output()
	if err != nil {
		return "", err
	}
	return string(out), nil
}

// [ISSUE: Path traversal — user-controlled userID in file path]
func GetUserAvatar(userID string) ([]byte, error) {
	return os.ReadFile(fmt.Sprintf("/var/data/avatars/%s.png", userID))
}

// [ISSUE: No authorization — any caller can delete any user]
func DeleteUser(store UserStore, targetID string) error {
	return store.Delete(targetID)
}
