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
	}
	return nil
}

// ─── Architecture: Layer violation + anemic domain ──────────────────
type User struct {
	ID        string
	Name      string
	Email     string
	Role      string
	Status    string
	CreatedAt time.Time
	LastLogin time.Time
}

// ─── FP: Hidden side effects ────────────────────────────────────────
func CountActiveUsers(users []User) int {
	count := 0
	for _, u := range users {
		if u.Status == "active" {
			count++
		}
	}

	data, _ := json.Marshal(map[string]int{"active_count": count})
	os.WriteFile("/tmp/user-stats.json", data, 0644)
	http.Post("https://analytics.internal/track", "application/json",
		bytes.NewReader(data))

	return count
}

// ─── Testability ────────────────────────────────────────────────────
type UserService struct {
}

func (s *UserService) IsInactive(user User, thresholdDays int) bool {
	return time.Since(user.LastLogin).Hours()/24 > float64(thresholdDays)
}

func (s *UserService) LoadConfig() (map[string]string, error) {
	data, err := os.ReadFile("/etc/app/users.json")
	if err != nil {
		return nil, err
	}
	var config map[string]string
	json.Unmarshal(data, &config)
	return config, nil
}

// ─── Clean Code ─────────────────────────────────────────────────────

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

func (s *UserService) GenerateReport(users []User) (string, error) {
	config, _ := s.LoadConfig()
	reportDir := config["report_dir"]

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

	os.WriteFile(fmt.Sprintf("%s/report_%s.txt", reportDir, time.Now().Format("20060102")),
		[]byte(report), 0644)

	return report, nil
}

func proc(d []map[string]interface{}, f string) []map[string]interface{} {
	var r []map[string]interface{}
	for _, x := range d {
		if e, ok := x["email"].(string); ok && e != "" {
			r = append(r, x)
		}
	}
	return r
}

func oldNotify(email string, msg string) {
	fmt.Printf("Sending to %s: %s\n", email, msg)
}

// ─── Security ───────────────────────────────────────────────────────
func ExportUserData(username string, format string) (string, error) {
	out, err := exec.Command("sh", "-c",
		fmt.Sprintf("user-export --user %s --format %s", username, format)).Output()
	if err != nil {
		return "", err
	}
	return string(out), nil
}

func GetUserAvatar(userID string) ([]byte, error) {
	return os.ReadFile(fmt.Sprintf("/var/data/avatars/%s.png", userID))
}

func DeleteUser(store UserStore, targetID string) error {
	return store.Delete(targetID)
}
