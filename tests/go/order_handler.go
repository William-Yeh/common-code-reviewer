// Test sample: Go HTTP + Gin order handler with intentional issues
// This file contains ~12 deliberate problems for the code review skill to catch.

package handlers

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"sync"

	"github.com/gin-gonic/gin"
)

// [ISSUE: Global mutable state — package-level variable]
var (
	db         *sql.DB
	orderCache = make(map[string]interface{})
	mu         sync.Mutex
)

// [ISSUE: No context.Context parameter]
func InitDB(dsn string) {
	var err error
	db, err = sql.Open("postgres", dsn)
	// [ISSUE: Error checked but only logged, execution continues with nil db]
	if err != nil {
		log.Println("failed to connect:", err)
	}
}

// [ISSUE: God function — handler does routing, validation, query, caching, notification]
func CreateOrder(c *gin.Context) {
	var body map[string]interface{}
	// [ISSUE: Using map[string]interface{} instead of a typed struct]
	c.ShouldBindJSON(&body)
	// [ISSUE: ShouldBindJSON error ignored]

	customerId := body["customer_id"].(string) // [ISSUE: Type assertion without ok check — will panic]

	// [ISSUE: SQL injection via fmt.Sprintf]
	query := fmt.Sprintf(
		"INSERT INTO orders (customer_id, product, quantity) VALUES ('%s', '%s', %v) RETURNING id",
		customerId,
		body["product"],
		body["quantity"],
	)

	var orderID string
	err := db.QueryRow(query).Scan(&orderID)
	if err != nil {
		c.JSON(500, gin.H{"error": "failed"}) // [ISSUE: Internal error message exposed, magic 500]
		return
	}

	mu.Lock()
	orderCache[orderID] = body
	mu.Unlock()

	// [ISSUE: Goroutine without lifecycle management — potential goroutine leak]
	go notifyWarehouse(body)

	c.JSON(200, gin.H{"id": orderID, "status": "created"})
}

func ListOrders(c *gin.Context) {
	// [ISSUE: No LIMIT, no pagination — unbounded query]
	rows, err := db.Query("SELECT id, customer_id, product, quantity FROM orders")
	if err != nil {
		c.JSON(500, gin.H{"error": err.Error()}) // [ISSUE: Leaking internal error to client]
		return
	}
	// [ISSUE: Missing defer rows.Close()]

	var orders []map[string]interface{}
	for rows.Next() {
		var id, customerId, product string
		var quantity int
		rows.Scan(&id, &customerId, &product, &quantity) // [ISSUE: Scan error ignored]

		// [ISSUE: N+1 query — querying items per order inside loop]
		itemRows, _ := db.Query( // [ISSUE: Error ignored with blank identifier]
			fmt.Sprintf("SELECT name, price FROM order_items WHERE order_id = '%s'", id),
		)
		var items []map[string]string
		for itemRows.Next() {
			var name string
			var price string
			itemRows.Scan(&name, &price)
			items = append(items, map[string]string{"name": name, "price": price})
		}

		orders = append(orders, map[string]interface{}{
			"id":          id,
			"customer_id": customerId,
			"items":       items,
		})
	}

	c.JSON(200, orders)
}

// [ISSUE: No context parameter — can't respect cancellation/timeout]
func notifyWarehouse(order map[string]interface{}) {
	data, _ := json.Marshal(order) // [ISSUE: Error ignored]

	// [ISSUE: No timeout, no context]
	resp, err := http.Post("http://warehouse-service/notify", "application/json",
		bytes.NewReader(data))
	if err != nil {
		// [ISSUE: Error logged but not wrapped with context]
		log.Println("warehouse notify failed:", err)
		return
	}
	defer resp.Body.Close()
}

func SetupRoutes() *gin.Engine {
	r := gin.Default()
	r.POST("/orders", CreateOrder)
	r.GET("/orders", ListOrders)
	return r
	// [ISSUE: No graceful shutdown setup, no server timeouts]
}
