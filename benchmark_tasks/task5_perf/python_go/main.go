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
	if len(a) == 0 || len(b) == 0 {
		return [][]float64{}
	}

	rowsA, colsA := len(a), len(a[0])
	rowsB, colsB := len(b), len(b[0])

	for _, row := range a {
		if len(row) != colsA {
			return [][]float64{}
		}
	}
	for _, row := range b {
		if len(row) != colsB {
			return [][]float64{}
		}
	}

	if colsA != rowsB || colsA == 0 || colsB == 0 {
		return [][]float64{}
	}

	result := make([][]float64, rowsA)
	for i := range result {
		result[i] = make([]float64, colsB)
	}

	var wg sync.WaitGroup
	for i := 0; i < rowsA; i++ {
		wg.Add(1)
		go func(row int) {
			defer wg.Done()
			defer func() {
				if r := recover(); r != nil {
					log.Printf("Recovered from panic in goroutine: %v", r)
				}
			}()
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
	if len(matrix) == 0 {
		return [][]float64{}
	}

	rows, cols := len(matrix), len(matrix[0])
	
	if cols == 0 {
		return [][]float64{}
	}

	for _, row := range matrix {
		if len(row) != cols {
			return [][]float64{}
		}
	}

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

type MultiplyRequest struct {
	A [][]float64 `json:"a"`
	B [][]float64 `json:"b"`
}

type MultiplyResponse struct {
	Result [][]float64 `json:"result"`
}

type TransposeRequest struct {
	Matrix [][]float64 `json:"matrix"`
}

type TransposeResponse struct {
	Result [][]float64 `json:"result"`
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

	if req.N <= 0 {
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(Response{Result: 0.0})
		return
	}

	result := computeHeavy(req.N)

	resp := Response{Result: result}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(resp)
}

func handleMultiply(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var req MultiplyRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, fmt.Sprintf("Invalid JSON: %v", err), http.StatusBadRequest)
		return
	}

	if len(req.A) == 0 || len(req.B) == 0 {
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(MultiplyResponse{Result: [][]float64{}})
		return
	}

	result := matrixMultiply(req.A, req.B)

	resp := MultiplyResponse{Result: result}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(resp)
}

func handleTranspose(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var req TransposeRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, fmt.Sprintf("Invalid JSON: %v", err), http.StatusBadRequest)
		return
	}

	if len(req.Matrix) == 0 {
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(TransposeResponse{Result: [][]float64{}})
		return
	}

	result := matrixTranspose(req.Matrix)

	resp := TransposeResponse{Result: result}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(resp)
}

func handleHealth(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]string{"status": "ok"})
}

func main() {
	http.HandleFunc("/compute", handleCompute)
	http.HandleFunc("/multiply", handleMultiply)
	http.HandleFunc("/transpose", handleTranspose)
	http.HandleFunc("/health", handleHealth)

	port := ":8080"
	log.Printf("Starting Go matrix computation server on %s", port)
	log.Fatal(http.ListenAndServe(port, nil))
}
