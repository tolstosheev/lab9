package main

import (
	"encoding/json"
	"fmt"
	"os"
)

type Person struct {
	Name    string `json:"name"`
	Age     int    `json:"age"`
	IsAdult bool   `json:"is_adult"`
}

func main() {
	var p Person

	if err := json.NewDecoder(os.Stdin).Decode(&p); err != nil {
		fmt.Fprintf(os.Stderr, "Error decoding JSON: %v\n", err)
		os.Exit(1)
	}

	p.IsAdult = p.Age >= 18

	w := json.NewEncoder(os.Stdout)
	if err := w.Encode(p); err != nil {
		fmt.Fprintf(os.Stderr, "Error encoding JSON: %v\n", err)
		os.Exit(1)
	}
}