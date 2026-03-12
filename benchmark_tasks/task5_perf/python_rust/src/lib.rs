use pyo3::prelude::*;
use rayon::prelude::*;

#[pyfunction]
fn matrix_multiply(a: Vec<Vec<f64>>, b: Vec<Vec<f64>>) -> Vec<Vec<f64>> {
    if a.is_empty() || b.is_empty() {
        return vec![];
    }
    
    let rows_a = a.len();
    let cols_a = a[0].len();
    let rows_b = b.len();
    let cols_b = b[0].len();

    if cols_a != rows_b || cols_a == 0 || cols_b == 0 {
        return vec![];
    }

    for row in &a {
        if row.len() != cols_a {
            return vec![];
        }
    }
    for row in &b {
        if row.len() != cols_b {
            return vec![];
        }
    }

    let mut result = vec![vec![0.0; cols_b]; rows_a];

    result.par_iter_mut().enumerate().for_each(|(i, row)| {
        for j in 0..cols_b {
            let mut sum = 0.0;
            for k in 0..cols_a {
                sum += a[i][k] * b[k][j];
            }
            row[j] = sum;
        }
    });

    result
}

#[pyfunction]
fn matrix_transpose(matrix: Vec<Vec<f64>>) -> Vec<Vec<f64>> {
    if matrix.is_empty() {
        return vec![];
    }
    
    let rows = matrix.len();
    let cols = matrix[0].len();
    
    if cols == 0 {
        return vec![];
    }

    for row in &matrix {
        if row.len() != cols {
            return vec![];
        }
    }

    let mut result = vec![vec![0.0; rows]; cols];

    for i in 0..rows {
        for j in 0..cols {
            result[j][i] = matrix[i][j];
        }
    }

    result
}

#[pyfunction]
fn compute_heavy(n: i32) -> PyResult<f64> {
    if n <= 0 {
        return Ok(0.0);
    }
    
    let n_size = n as usize;

    let a: Vec<Vec<f64>> = (0..n_size)
        .map(|i| (0..n_size).map(|j| (i + j) as f64).collect())
        .collect();
    
    let b: Vec<Vec<f64>> = (0..n_size)
        .map(|i| (0..n_size).map(|j| (i * j + 1) as f64).collect())
        .collect();

    let product = matrix_multiply(a, b);

    if product.is_empty() {
        return Ok(0.0);
    }

    let transposed = matrix_transpose(product);
    let total: f64 = transposed.iter().flatten().sum();

    Ok(total)
}

#[pymodule]
fn matrix_ops_rust(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(compute_heavy, m)?)?;
    m.add_function(wrap_pyfunction!(matrix_multiply, m)?)?;
    m.add_function(wrap_pyfunction!(matrix_transpose, m)?)?;
    Ok(())
}