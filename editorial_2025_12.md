# Coroutines

You've likely heard about this new C++20 feature, **coroutines**. I think that this is a really important subject and there are several cool use-cases for coroutines. A **coroutine** in the simplest terms is just a function that you can pause in the middle. At a later point the caller will decide to resume the execution of the function right where you left off. Unlike a function therefore, coroutines are always stateful - you atleast need to remember where you left off in the function body. 

Coroutines can simplify our code! Coroutines are a great tool, when it comes to implementing parsers.

### The coroutine return type

The initial call to the coroutine function will produce this return object of a certain `ReturnType` and hand it back to the caller. The interface of this type is what is going to determine what the coroutine is capable of. Since coroutines are super-flexible, we can do a whole lot with this return object. If you have some coroutine, and you want to understand what it's doing, the first thing you should look at is the `ReturnType`, and what it's interface is. The important thing here is, we design this `ReturnType`. If you are writing a coroutine, you can decide, what goes into this interface.

### How to turn a function into a coroutine?

The compiler looks for one of the three keywords in the implementation: `co_yield`, `co_await` and `co_return`.

| Keyword | Action | State |
|---------|--------|-------|
| `co_yield` | Output | Suspended |
| `co_return` | Output | Ended |
| `co_await` | Input | Suspended |

In the preceding table, we see that after `co_yield` and `co_await`, the coroutine suspends itself and after `co_return`, it is terminated (`co_return` is the equivalent of the `return` statement in the C++ function).

### Use-cases for coroutines 

**Asynchronous computation.** Suppose we are tasked with designing a simple echo server. We listen for incoming data from a client socket and we simply send it back to the client. At some point in our code for the echo server, we will have a piece of logic like below:

```cpp
void session(Socket sock){
    char buffer[1024];
    int len = sock.read({buffer});
    sock.write({buffer,len});
    log(buffer);
}
```

we certainly don't want to write a server like this. Say one of the clients requests communication and we are in a session. They say, they are ready to send the data, so we are blocking on the `read`, but maybe they send us this data in $2$ minutes, or $5$ minutes or even more. And other clients keep waiting.

One solution is to use an asynchronous framework and rewrite our code as follows:

```cpp
void session(Socket sock){
    struct State{ Socket sock; char buffer[1024]; };
    
    // Heap allocate the state
    auto state = std::make_shared<State>(sock, buffer);

    auto on_read_finished_callback = [state](
        error_code ec, 
        size_t len
    )
    {
        auto done = [state](error_code ec, size_t len)
        {
            if(!ec)
                log();
        }
        if(!ec)
        {
            // Perform an asynchronous write
            state->socket.async_write( 
                state->buffer, 
                done 
            );    
        }
    }

    // Perform an asynchronous read 
    state->socket.async_read( state->buffer, 
                             on_read_finished_callback );
}
```

So, the `session` makes two associations: 

$$
\begin{align*}
\text{On finishing read} &\mapsto \texttt{on\_finished\_read\_callback} \\
\text{On finishing write} &\mapsto \texttt{done} \\
\text{Accepting a new client connection} &\mapsto \texttt{session}
\end{align*}
$$

And implicitly there is a third association even though we cannot see it here - this entire function `session` is most likely a callback, in response to an event like $\text{On client connection established}$. So, the server will be many different associations of events to callbacks at different levels. 

Pay attention to the `state`. We said that, we wanted to allocate it on the heap and manage it through a `shared_ptr`. We pass this `shared_ptr<State>` by value to every single callback. This way, I make sure that the last one who touches this session turns off the lights and deallocates `state`. 

While this is a toy-example, in real production code, there can be a long sequence of steps and calling lambdas inside lambdas can obfuscate the meaning of the code. 

A coroutine implementation of the same echo'ing session would look like this:

```cpp
Task<void> session(Socket sock){
    char buffer[1024];
    int len = co_await sock.async_read({buffer});
    co_await sock.async_write({buffer,len});
    log(buffer);
}
```

This looks very similar to the sequential code, except that we use this `co_await` keyword. You have clear indication of the points where the coroutine will be suspended. Also, note that previously the function `session` returned `void`. Now, we are returning something - a `Task<void>`. This will be a handle to the coroutine and it's how the outside world will be communicating with the coroutine. 

**Suspended computation**. A second use-case is that coroutines support lazy evaluation. Lazy evaluation doesn't do any work unless it's absolutely necessary. This can also potentially make your code more efficient. Lazy evaluation also supports programming with infinite lists. 

## The simplest coroutine

The following code is the simplest implementation of a coroutine:

```cpp
#include <coroutine>
void coro_func(){
    co_return;
}

int main(){
    coro_func();
}
```

[Compiler Explorer](https://compiler-explorer.com/z/W3GoWPoEs)

Our first coroutine will just return nothing. It will not do anything else. Sadly, the preceding code is too simple for a functional coroutine and it will not compile. When compiling with `gcc 15.2`, we get the following error:

```shell
<source>: In function 'void coro_func()':
<source>:4:5: error: unable to find the promise type for this coroutine
    4 |     co_return;
      |     ^~~~~~~~~
```

Looking at C++ reference, we see that the return type of a coroutine must define a type named `promise_type`. 

### The `promise_type`

Why do we need a promise? The `promise_type` is the second important piece in the coroutine mechanism. We can draw an analogy from futures and promises which are essential blocks for achieving asynchronous programming in C++. The future is the thing, that the function that does the asynchronous computation, hands out back to the caller, that the caller can use to retrieve the result by invoking the `get()` member function. The future has the role of the return object. But, you need something that remains on the producer-side. The asynchronous function holds on to the promise, and that's where it puts the results that will be given to the caller, when it calls `get()` on the future. The idea behind the `promise_type` for coroutines is similar. The promise is where the coroutine's return value is stored, and it provides functions to control the coroutine's behavior at startup and completion of t he coroutine. The promise is the interface through which the caller interacts with the coroutine.

Following the reference advice, we can write a new version of our coroutine.

```cpp
#include <coroutine>
struct Task
{
    struct promise_type
    {
    };
};

Task coro_func(){
    co_return;
}

int main(){
    coro_func();
}
```

Note that the return type of a coroutine can have any name (I call it `Task`, so that it makes intuitive sense). Compiling the preceding code again gives us errors. All errors are about missing functions in the `promise_type`:

```shell
<source>: In function 'Task coro_func()':
<source>:11:5: error: no member named 'return_void' in
'std::__n4861::__coroutine_traits_impl<Task, void>::promise_type' {aka 'Task::promise_type'}
   11 |     co_return;
      |     ^~~~~~~~~
<source>:10:6: error: no member named 'unhandled_exception' in
'std::__n4861::__coroutine_traits_impl<Task, void>::promise_type' {aka 'Task::promise_type'}
   10 | Task coro_func(){
      |      ^~~~~~~~~
<source>:10:6: error: no member named 'get_return_object' in
'std::__n4861::__coroutine_traits_impl<Task, void>::promise_type' {aka 'Task::promise_type'}
```

One of the important functions of the `promise_type` is that it determines what happens at certain key points in the coroutine's life. It determines, what happens at the startup and completion of execution of the coroutine. 

### Implementing the `promise_type`

The first thing that the compiler expects from us the `get_return_object()` function. The return type of this function is the same as the return type of the coroutine.

```cpp
#include <coroutine>
#include <print>

struct Task{
    struct promise_type{
        Task get_return_object(){
            std::println("get_return_object()");
            return Task{ *this };
        }

        void return_void() noexcept {
            std::println("return_void()");
        }

        void unhandled_exception() noexcept {
            std::println("unhandled_exception()");
        }

        std::suspend_always initial_suspend() noexcept{
            std::println("initial_suspend()");
            return {};
        }

        std::suspend_always final_suspend() noexcept{
            std::println("final_suspend()");
            return {};
        }
    };

    explicit Task(promise_type&){
        std::println("Task(promise_type&)");
    }

    ~Task() noexcept{
        std::println("~Task()");
    }
};

Task coro_func(){
    co_return;
}

int main(){
    coro_func();
}
```

Output:
```shell
get_return_object()
Task(promise_type&)
initial_suspend()
~Task()
```

The `get_return_object()` method is implicitly called when the coroutine starts executing. Its upto the `promise_type` to provide an implementation of this method that constructs the return object that will be handed back to the caller. The `Task` object is stored on the heap. You don't see this in the source code anywhere. When the coroutine reaches its first suspension point, and control flow is returned back to the caller, then the caller will receive this object.

The  `return_void()` function is a customization point for handling what happens when we reach the `co_return` statement in the function body. There is also a corresponding `return_value()`, if you don't have an empty `co_return` statement, but we'll look at this at length later ahead.

The  `unhandled_exception()` is similar to the `return_void()`, this function is a customization point for handling, what happens when the coroutine throws an exception. We leave it empty for now.

We need to implement two more functions `initial_suspend()` and `final_suspend()`. These are basically the customization points that allow us to execute some code, both when the coroutine first starts executing and shortly before the coroutine ends execution. Here, we are returning `std::suspend_always` which basically means that at these points, I want to go into suspension.

In a typical implementation, you either return `std::suspend_always`, which means you pause execution at this point and hand control back to the caller always, or you return `std::suspend_never`, which basically means you just go on and continue executing the coroutine.

Note that, `final_suspend()` is not printed in the output, because the coroutine is paused at `initial_suspend()` and since I never resumed it, I don't see the output on the console. 

## A yielding coroutine

Let's implement another coroutine that can send data back to the caller. In this second example, we implement a coroutine that produces a message. It will be the hello world of coroutines. The coroutine will say hello and the caller function will print the message received from the coroutine.

To implement this functionality, we need to establish a communication channel from the coroutine to the caller. This channel is the mechanism that allows the coroutine to pass values to the caller and receive information from it. This channel is established through the coroutine's `promise_type` and the *coroutine handle*.

The *coroutine handle* is a type that gives access to the coroutine frame(the coroutine's internal state) and allows the caller to resume or destroy the coroutine. The handle is what the caller can use to resume the coroutine after it has been suspended (for example after `co_await` or `co_yield`). The handle can also be used to check whether the coroutine is done or to clean up its resources.

The following code is the new version of both the caller function and the coroutine:

```cpp
Task coro_func(){
    co_yield "Hello world from the coroutine";
    co_return;
}

int main(){
    auto task = coro_func();
    std::print("task.get() = {}", task.get());
    return 0;
}
```

The coroutine *yields* and sends some data to the caller. The caller reads that data and prints it. When the compiler reads the `co_ yield` expression, it will generate a call to the `yield_value` function defined in the `promise_type`. Thus, we add the following code to the `promise_type` :

```cpp
struct Task{
    struct promise_type{
        std::string output_data;

        /* ... */
        std::suspend_always yield_value(std::string msg) noexcept{
            output_data = std::move(msg);
        }
    };

    explicit Task(promise_type&){
        std::println("Task(promise_type&)");
    }

    ~Task() noexcept{
        std::println("~Task()");
    }
};
```

The function gets a `std::string` object and moves it to the `output_data` member variable of the promise type. But, this just keeps the data inside the `promise_type`. We still need a mechanism to get that data out of the coroutine.

### The coroutine handle

Once we require a communication channel to and from a coroutine, we need a way to refer to a suspended or executing coroutine. The mechanism to refer to the coroutine object is through a pointer or handle called a **coroutine handle**. The C++ library header file `<coroutine>` defines a type `std::coroutine_handle` to work with coroutine handles. 

Two functions are of interest to us in the `std::coroutine_handle` interface : `resume()` and `destroy()`. 

```cpp
struct coroutine_handle<promise_type>{
    /* ... */
    void resume() const;
    void destroy() const;
    promise_type& promise() const;
    static coroutine_handle from_promise(promise_type&);
}
```

What `resume()` does is simply, it resumes the suspended coroutine. It continues execution. 

If we think of this coroutine frame or object living somewhere on the heap, where all of the state of execution is stored, one way to destroy this state is to let the coroutine run to completion. But, far more commonly, we would like to manage the lifetime externally and we can then just call the `destroy()` function which will then get rid of the coroutine state.

Note that, the `coroutine_handle` is not a smart pointer type. So, you have to call the `destroy()` explicitly. 

There's two more functions `.promise()` and `.from_promise()`. These are used to convert from a coroutine to a promise object and vice versa.

We add the following functionality to our return type to manage the coroutine handle:

```cpp
struct Task{
    struct promise_type{
        std::string output_data;
        /* ... */
        std::suspend_always yield_value(std::string msg) noexcept{
            output_data = std::move(msg);
        }
    };

    // Coroutine handle member-variable
    std::coroutine_handle<promise_type> handle{};

    explicit Task(promise_type& promise)
    : handle { std::coroutine_handle<promise_type>::from_promise(promise) }
    {
        std::println("Task(promise_type&)");
    }

    // Destructor
    ~Task() noexcept{
        std::println("~Task()");
        if(handle)
            handle.destroy();
    }
};
```
The preceding code declares a coroutine handle of type `std::coroutine_handle<promise_type>` and creates the handle in the return type constructor. The handle is destroyed in the return type destructor. 

Now, back to our yielding coroutine. The only missing bit is a `get()` function for the caller to be able to extract the resultant string out of the promise.

```cpp
std::string get(){
    if(!handle.done()){
        handle.resume();
    }
    return std::move(handle.promise().output_data);
}
```

The `get()` function resumes the coroutine if it has not terminated and return the result stored in the `output_data` member variable of the promise. The full source code listing is shown below:

```cpp
#include <coroutine>
#include <print>
#include <iostream>
#include <string>

using namespace std::string_literals;

struct Task{
    struct promise_type{
        std::string output_data{};

        Task get_return_object(){
            std::println("get_return_object()");
            return Task{ *this };
        }

        void return_void() noexcept {
            std::println("return_void()");
        }

        void unhandled_exception() noexcept {
            std::println("unhandled_exception()");
        }

        std::suspend_always initial_suspend() noexcept{
            std::println("initial_suspend()");
            return {};
        }

        std::suspend_always final_suspend() noexcept{
            std::println("final_suspend()");
            return {};
        }

        std::suspend_always yield_value(std::string msg) noexcept{
            std::println("yield_value(std::string)");
            output_data = std::move(msg);
            return {};
        }
    };

    // Coroutine handle member-variable
    std::coroutine_handle<promise_type> handle{};

    explicit Task(promise_type& promise)
    : handle { std::coroutine_handle<promise_type>::from_promise(promise) }
    {
        std::println("Task(promise_type&)");
    }

    ~Task() noexcept{
        std::println("~Task()");
        if(handle)
            handle.destroy();
    }

    std::string get(){
        std::println("get()");
        if(!handle.done())
            handle.resume();

        return std::move(handle.promise().output_data);
    }
};

Task coro_func(){
    co_yield "Hello world from the coroutine";
    co_return;
}

int main(){
    auto task = coro_func();
    std::cout << task.get() << std::endl;
}
```

Output:

```shell
get_return_object()
Task(promise_type&)
initial_suspend()
get()
yield_value(std::string)
Hello world from the coroutine
~Task()
```

The output shows what is happening during the coroutine execution. The `Task` object is created after a call to `get_return_object`. The coroutine is initially suspended. The caller wants to get the message from the coroutine so `get()` is called, which resumes the coroutine. When the compiler sees `co_yield` statement in the coroutine, it generates an implicit called to `yield_value(std::string)`. `yield_value` is called and the message is copied to the resultant member variable `output_data` in the promise. Finally, the message is printed by the caller function, and the coroutine returns. 

## A waiting coroutine

We are now going to implement a coroutine that can wait for the input data sent by the caller. In our example, the coroutine will wait until it gets a `std::string` object and then print it. We say that the coroutine waits, we mean it is suspended (that is, not executed) until the data is received.

We start with changes to both the coroutine and the caller function:

```cpp
Task coro_func(){
    std::cout << co_await std::string{};
    co_return;
}

int main(){
    auto task = coro_func();
    task.put("To boldly go where no man has gone before");
    return 0;
}
```

In the preceding code, the caller function calls the `put()` function(a method in the return type structure) and the coroutine calls `co_await` to wait for a `std::string` object from the caller.

The changes to the return type are simple, that is, just adding the `put()` function.

```cpp
void put(std::string msg){
    handle.promise().input_data = std::move(msg);
    if(!handle.done()){
        handle.resume();
    }
}
```

We need to add the `input_data` variable to the promise structure. But, just with those changes to our first example and the coroutine handle from the previous example, the code cannot be compiled.


```cpp
#include <print>
#include <string>
#include <coroutine>
#include <iostream>

struct Task{
    struct promise_type{
        std::string input_data{};

        Task get_return_object() noexcept{
            std::println("get_return_object");
            return Task{ *this };
        } 

        void return_void() noexcept{
            std::println("return_void");
        }

        std::suspend_always initial_suspend() noexcept{
            std::println("initial_suspend");
            return {};
        }

        std::suspend_always final_suspend() noexcept{
            std::println("final_suspend");
            return {};
        }
        void unhandled_exception() noexcept{
            std::println("unhandled_exception");
        }

        std::suspend_always yield_value(std::string msg) noexcept{
            std::println("yield_value");
            //output_data = std::move(msg);
            return {};
        }
    };

    std::coroutine_handle<promise_type> handle{};

    explicit Task(promise_type& promise)
    : handle{ std::coroutine_handle<promise_type>::from_promise(promise)}
    {
        std::println("Task(promise_type&) ctor");
    }

    ~Task() noexcept{
        if(handle)
            handle.destroy();

        std::println("~Task()");
    }

    void put(std::string msg){
        handle.promise().input_data = std::move(msg);
        if(!handle.done())
            handle.resume();
    }
};

Task coro_func(){
    std::cout << co_await std::string{};
    co_return;
}

int main(){
    auto task = coro_func();
    task.put("To boldly go where no man has gone before");
    return 0;
}
```

The compiler gives us the following error:

```shell
<source>: In function 'Task coro_func()':
<source>:62:18: error: no member named 'await_ready' in 'std::string' {aka 'std::__cxx11::basic_string<char>'}
   62 |     std::cout << co_await std::string{};
      |                  ^~~~~~~~
```

Let's explore more about what this error message means.

## What is an awaitable?

An *awaitable* is any object, I can call `co_await` on. You can think of `co_await` like an operator, and its argument as an *awaitable*. The way to think about the operator `co_await` is that these are opportunities for suspension. These are the points where the coroutine can be paused. Similar to, how the `promise_type` provides hooks to control what happens at startup or when you return from the coroutine, the awaitable provides these hooks for what happens when we go into suspension. 

```cpp
struct Awaitable{
    bool await_ready();
    void await_suspend(std::coroutine_handle<promise_type>);
    void await_resume(std::coroutine_handle<promise_type>);
};
```

The first function is `.await_ready()` which returns a `bool`. This determines whether we do actually go into suspension or we just say, *yeah, we are ready, and we don't want to go into suspension*, we want to continue execution and in that case we just return `true`.

The next function is `.await_suspend()` and that is the customization point that will get executed shortly before the coroutine function goes to sleep. 

The next function is `.await_resume()` and that is the customization point that will get execute just after the coroutine is resumed.

The following code shows our implementation of the `await_transform` function and the `Awaitable` struct:

```cpp
auto await_transform(std::string) noexcept{
    struct Awaitable{
        promise_type& promise;

        bool await_ready() const noexcept{
            return true;    // Says, yeah we are ready
                            // we don't need to sleep. Just go on.
        }

        std::string await_resume() const noexcept{
            return std::move(promise.input_data);
        }

        void await_suspend(std::coroutine_handle<promise_type>) const noexcept{}
    };

    return Awaitable(*this);
}
```

This is the code for the full example of the waiting coroutine:

```cpp
#include <print>
#include <string>
#include <coroutine>
#include <iostream>

struct Task{
    struct promise_type{
        std::string input_data{};

        Task get_return_object() noexcept{
            std::println("get_return_object");
            return Task{ *this };
        } 

        void return_void() noexcept{
            std::println("return_void");
        }

        std::suspend_always initial_suspend() noexcept{
            std::println("initial_suspend");
            return {};
        }

        std::suspend_always final_suspend() noexcept{
            std::println("final_suspend");
            return {};
        }
        void unhandled_exception() noexcept{
            std::println("unhandled_exception");
        }

        std::suspend_always yield_value(std::string msg) noexcept{
            std::println("yield_value");
            //output_data = std::move(msg);
            return {};
        }

        auto await_transform(std::string) noexcept{
            struct Awaitable{
                promise_type& promise;

                bool await_ready() const noexcept{
                    return true;    // Says, yeah we are ready
                                    // we don't need to sleep. Just go on.
                }

                std::string await_resume() const noexcept{
                    return std::move(promise.input_data);
                }

                void await_suspend(std::coroutine_handle<promise_type>) const noexcept{}

            };
            
            return Awaitable(*this);
        }
    };

    std::coroutine_handle<promise_type> handle{};

    explicit Task(promise_type& promise)
    : handle{ std::coroutine_handle<promise_type>::from_promise(promise)}
    {
        std::println("Task(promise_type&) ctor");
    }

    ~Task() noexcept{
        if(handle)
            handle.destroy();

        std::println("~Task()");
    }

    void put(std::string msg){
        handle.promise().input_data = std::move(msg);
        if(!handle.done())
            handle.resume();
    }
};

Task coro_func(){
    std::cout << co_await std::string{};
    co_return;
}

int main(){
    auto task = coro_func();
    task.put("To boldly go where no man has gone before");
    return 0;
}
```

Output:
```shell
get_return_object
Task(promise_type&) ctor
initial_suspend
To boldly go where no man has gone beforereturn_void
final_suspend
~Task()
```

## Coroutine Generators

A **generator** is a coroutine that generates a sequence of elements by repeatedly resuming itself from the point that it was suspended.

A generator can be seen as an infinite list, because it can generate an arbitrary number of elements.

Implementing even the most basic coroutine in C++ requires a certain amount of code. C++23 introduced the `std::generator` template class. I present below the source code for a simple `FibonacciGenerator`. 

```cpp
#include <print>
#include <generator>

std::generator<int> makeFibonacciGenerator(){
    int i1{0};
    int i2{1};
    while(true){
        co_yield i1;
        i1 = std::exchange(i2, i1 + i2);
    }
    co_return;
}

int main(){
    auto fibo_gen = makeFibonacciGenerator();
    std::println("The first 10 numbers the Fibonacci sequence are : ");
    int i{0};
    for(auto f = fibo_gen.begin(); f!=fibo_gen.end();++f){
        if(i  == 10)
            break;
        std::println("F[{}] = {}", i, *f);
        ++i;
    }
    return 0;
}
```
