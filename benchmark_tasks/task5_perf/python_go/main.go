package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"sync"
)

type Request struct {
	N int `json:"n"`
}

type Response struct {
	Result float64 `json:"result"`
}

func matrixMultiply(a, b [][]float64) [][]float64 {
	rowsA, colsA := len(a), len(a[0])
	colsB := len(b[0])

	result := make([][]float64, rowsA)
	for i := range result {
		result[i] = make([]float64, colsB)
	}

	var wg sync.WaitGroup
	for i := 0; i < rowsA; i++ {
		wg.Add(1)
		go func(row int) {
			defer wg.Done()
			for j := 0; j < colsB; j++ {
				sum := 0.0
				for k := 0; k < colsA; k++ {
					sum += a[row][k] * b[k][j]
				}
				result[row][j] = sum
			}
		}(i)
	}
	wg.Wait()

	return result
}

func matrixTranspose(matrix [][]float64) [][]float64 {
	rows, cols := len(matrix), len(matrix[0])
	result := make([][]float64, cols)
	for i := range result {
		result[i] = make([]float64, rows)
	}

	for i := 0; i < rows; i++ {
		for j := 0; j < cols; j++ {
			result[j][i] = matrix[i][j]
		}
	}

	return result
}

func computeHeavy(n int) float64 {
	a := make([][]float64, n)
	b := make([][]float64, n)
	for i := 0; i < n; i++ {
		a[i] = make([]float64, n)
		b[i] = make([]float64, n)
		for j := 0; j < n; j++ {
			a[i][j] = float64(i + j)
			b[i][j] = float64(i*j + 1)
		}
	}

	product := matrixMultiply(a, b)

	transposed := matrixTranspose(product)

	total := 0.0
	for _, row := range transposed {
		for _, val := range row {
			total += val
		}
	}

	return total
}

func handleCompute(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var req Request
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, fmt.Sprintf("Invalid JSON: %v", err), http.StatusBadRequest)
		return
	}

	result := computeHeavy(req.N)

	resp := Response{Result: result}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(resp)
}

func handleHealth(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]string{"status": "ok"})
}

func main() {
	http.HandleFunc("/compute", handleCompute)
	http.HandleFunc("/health", handleHealth)

	port := ":8080"
	log.Printf("Starting Go matrix computation server on %s", port)
	log.Fatal(http.ListenAndServe(port, nil))
}
