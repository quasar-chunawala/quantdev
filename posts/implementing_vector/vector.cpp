// Write your solution here
// C++20 for C++
#include <gtest/gtest.h>
#include <cstddef>
#include <cstdint>
#include <format>
#include <initializer_list>
#include <memory>
#include <print>
#include <stdexcept>
#include <type_traits>
#include <utility>

namespace dev {
    template <typename T>
    class vector {
        using value_type = T;
        using size_type = std::size_t;
        using pointer = T*;
        using const_pointer = const T*;
        using reference = T&;
        using const_reference = const T&;
        using iterator = pointer;
        using const_iterator = const_pointer;
        constexpr static std::size_t initial_capacity{1};

    private:
        pointer m_data;
        size_type m_size;
        size_type m_capacity;

    public:

        iterator begin(){ return m_data; }
        const_iterator begin() const{ return m_data; }
        iterator end(){ return begin() + m_size; }
        const_iterator end() const{ return begin() + m_size; }
        
        size_type size() const { return m_size; }
        size_type capacity() const { return m_capacity; }

        vector()
        : m_data{static_cast<T*>(operator new(sizeof(T)))},
        m_size{0},
        m_capacity{initial_capacity} {}

        vector(size_t n, const T& initial_value)
        : m_data{static_cast<T*>(operator new(sizeof(T) * n))},
        m_size{0},
        m_capacity{n} {
            try {
                std::uninitialized_fill_n(m_data, n, initial_value);
                m_size = n;
            } catch (std::exception& ex) {
                operator delete(m_data);
                m_capacity = 0;
            }
        }

        vector(std::initializer_list<T> list)
        : m_data{static_cast<T*>(operator new(sizeof(T) *
                                                    list.size()))},
        m_size{list.size()},
        m_capacity{list.size()} {
            try {
                if constexpr (std::is_nothrow_move_constructible_v<T>) {
                    std::uninitialized_move(list.begin(), list.end(), m_data);
                } else {
                    std::uninitialized_copy(list.begin(), list.end(), m_data);
                }
            } catch (std::exception& ex) {
                operator delete(m_data);
                m_size = 0;
                m_capacity = 0;
            }
        }

        vector(const vector& other)
        : m_data{operator new(sizeof(T) * other.size())},
        m_size{other.size()},
        m_capacity{other.capacity()} {
            try {
                // Perform a deep-copy of all the Ts
                std::uninitialized_copy(other.m_data, other.m_data + other.m_size,
                                        m_data);
            } catch (std::exception& ex) {
                operator delete(m_data);
                std::string error_msg =
                    std::format("Error while copying in copy ctor {}", ex.what());
                throw std::logic_error(error_msg);
            }
        }

        vector(vector&& other) noexcept
        : m_data{std::exchange(other.m_data, nullptr)},
        m_size{std::exchange(other.m_size, 0)},
        m_capacity{std::exchange(other.m_capacity, 0)} 
        {}

        void swap(vector& other) noexcept {
            std::swap(this->m_data, other.m_data);
            std::swap(this->m_size, other.m_size);
            std::swap(this->m_capacity, other.m_capacity);
        }

        vector& operator=(const vector& other) {
            vector(other).swap(*this);
            return *this;
        }

        vector& operator=(vector&& other) {
            vector(std::move(other)).swap(*this);
            return *this;
        }

        bool is_full() { return size() == capacity(); }
        bool empty() { return m_size == 0; }

        void push_back(T value) {
            std::size_t offset = size();
            if (m_size == m_capacity - 1) {
                // Allocate new memory
                std::size_t new_size = size() + 1;
                std::size_t new_capacity = 3 * m_capacity;
                T* new_memory_block = static_cast<T*>(operator new(
                    sizeof(T) * new_capacity));
                T* ptr_to_new_T{nullptr};

                try {
                    // Construct the new T in new memory block
                    ptr_to_new_T =
                        new (new_memory_block + offset) T(value);
                } catch (std::exception& ex) {
                    operator delete(new_memory_block);
                    std::string error_msg = std::format(
                        "Failed to copy-construct T : {}", ex.what());
                    throw std::logic_error(error_msg);
                }

                try {
                    // Copy/move- the Ts from the old storage to new
                    if constexpr (std::is_nothrow_move_constructible_v<T>) {
                        std::uninitialized_move(m_data, m_data + offset,
                                                new_memory_block);
                    } else {
                        std::uninitialized_copy(m_data, m_data + offset,
                                                new_memory_block);
                    }
                } catch (std::exception& ex) {
                    std::destroy_at(ptr_to_new_T);
                    operator delete(new_memory_block);
                    std::string error_msg = std::format(
                        "Failed to copy/move data from old to new storage, "
                        "exception : {}",
                        ex.what());
                    throw std::logic_error(error_msg);
                }

                // Destroy the objects in the old storage
                auto p{m_data};
                for (auto p{m_data}; p < m_data + m_size; ++p) {
                    p->~T();
                }

                // Deallocate old storage
                operator delete(m_data);

                // Reassign internal buffer pointer and update size and capacity
                m_data = new_memory_block;
                m_size = new_size;
                m_capacity = new_capacity;
            } else {
                try {
                    std::construct_at(m_data + offset, value);
                    m_size += 1;
                } catch (std::exception& ex) {
                    std::string error_msg = std::format(
                        "Failed to copy-construct T, exception : {}",
                        ex.what());
                    throw std::logic_error(error_msg);
                }
            }
        }
        
        reference operator[](size_type idx){
            return m_data[idx];
        }

        const_reference operator[](size_type idx) const{
            return m_data[idx];
        }

        // precondition: !empty()
        reference front(){ return (*this)[0]; }
        const_reference front() const { return (*this)[0]; }
        reference back(){ return (*this)[m_size - 1]; }
        const_reference back() const{ return (*this)[m_size - 1]; }

        const T& at(std::size_t index) const {
            if (index < 0 || index >= m_size)
                throw std::out_of_range("Array index out of bounds!");

            return m_data[index];
        }
        void shrink_to_fit() {
            // Allocate a new memory block of capacity = m_size
            T* new_memory_block =
                static_cast<T*>(operator new(sizeof(T) * m_size));

            try {
                // Copy/move the Ts from the old storage to new storage
                if constexpr (std::is_nothrow_move_constructible_v<T>) {
                    std::uninitialized_move(m_data, m_data + m_size,
                                            new_memory_block);
                } else {
                    std::uninitialized_copy(m_data, m_data + m_size,
                                            new_memory_block);
                }
            } catch (std::exception& ex) {
                operator delete(new_memory_block);
                std::string error_msg = std::format(
                    "Internal error in shrink_to_fit() : {}", ex.what());
                throw std::logic_error(error_msg);
            }

            // Destroy objects in old storage and deallocate memory
            for (auto p{m_data}; p < m_data + m_size; ++p) {
                std::destroy_at<T>(p);
            }
            // Deallocate memory
            operator delete(m_data);

            // Reassign internal buffer pointer and set size and capacity
            m_data = new_memory_block;
            m_capacity = m_size;
        }
        void pop_back() {
            T* ptr_to_last = m_data + m_size - 1;
            std::destroy_at(ptr_to_last);
            --m_size;
        }
    };
}  // namespace dev

TEST(VectorTest, DefaultConstructorTest) {
    dev::vector<int> v;
    EXPECT_EQ(v.empty(), true);
}

TEST(VectorTest, InitializerListTest){
    dev::vector<int> v{1, 2, 3, 4, 5};
    EXPECT_EQ(!v.empty(), true);
    EXPECT_EQ(v.size(), 5);
    EXPECT_TRUE(v.capacity() > 0);
    for(auto i{0uz}; i < v.size(); ++i){
        EXPECT_EQ(v.at(i), i+1);
    }
}

TEST(VectorTest, ParameterizedConstructorTest){
    dev::vector v(10, 5.5);
    EXPECT_EQ(v.size(), 10);
    for(auto i{0uz}; i < v.size(); ++i){
        EXPECT_EQ(v[i], 5.5);
    }
}

int main(int argc, char** argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}