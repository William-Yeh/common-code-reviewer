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

var (
	db         *sql.DB
	orderCache = make(map[string]interface{})
	mu         sync.Mutex
)

func InitDB(dsn string) {
	var err error
	db, err = sql.Open("postgres", dsn)
	if err != nil {
		log.Println("failed to connect:", err)
	}
}

func CreateOrder(c *gin.Context) {
	var body map[string]interface{}
	c.ShouldBindJSON(&body)

	customerId := body["customer_id"].(string)

	query := fmt.Sprintf(
		"INSERT INTO orders (customer_id, product, quantity) VALUES ('%s', '%s', %v) RETURNING id",
		customerId,
		body["product"],
		body["quantity"],
	)

	var orderID string
	err := db.QueryRow(query).Scan(&orderID)
	if err != nil {
		c.JSON(500, gin.H{"error": "failed"})
		return
	}

	mu.Lock()
	orderCache[orderID] = body
	mu.Unlock()

	go notifyWarehouse(body)

	c.JSON(200, gin.H{"id": orderID, "status": "created"})
}

func ListOrders(c *gin.Context) {
	rows, err := db.Query("SELECT id, customer_id, product, quantity FROM orders")
	if err != nil {
		c.JSON(500, gin.H{"error": err.Error()})
		return
	}

	var orders []map[string]interface{}
	for rows.Next() {
		var id, customerId, product string
		var quantity int
		rows.Scan(&id, &customerId, &product, &quantity)

		itemRows, _ := db.Query(
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

func notifyWarehouse(order map[string]interface{}) {
	data, _ := json.Marshal(order)

	resp, err := http.Post("http://warehouse-service/notify", "application/json",
		bytes.NewReader(data))
	if err != nil {
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
}

// Serve runs the order API until the process is killed.
func Serve(addr string) error {
	return SetupRoutes().Run(addr)
}
