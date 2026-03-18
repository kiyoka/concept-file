#include <vector>
#include <stdexcept>
#include <iostream>

namespace linalg {

class Matrix {
    std::vector<std::vector<double>> data;
    int rows;
    int cols;

public:
    Matrix(int rows, int cols);
    Matrix(int rows, int cols, double initial);

    double get(int r, int c) const;
    void set(int r, int c, double value);

    Matrix multiply(const Matrix &other) const;
    Matrix transpose() const;
    Matrix add(const Matrix &other) const;

    int getRows() const;
    int getCols() const;

    void print() const;
};

Matrix Matrix::multiply(const Matrix &other) const {
    if (cols != other.rows) {
        throw std::invalid_argument("Incompatible dimensions");
    }
    Matrix result(rows, other.cols, 0.0);
    for (int i = 0; i < rows; i++) {
        for (int j = 0; j < other.cols; j++) {
            double sum = 0;
            for (int k = 0; k < cols; k++) {
                sum += data[i][k] * other.data[k][j];
            }
            result.set(i, j, sum);
        }
    }
    return result;
}

Matrix Matrix::transpose() const {
    Matrix result(cols, rows);
    for (int i = 0; i < rows; i++) {
        for (int j = 0; j < cols; j++) {
            result.set(j, i, data[i][j]);
        }
    }
    return result;
}

}  // namespace linalg
