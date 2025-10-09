### PyCombinator Programming Language Interpreter PRD

#### 1. Requirement Overview
This project aims to develop a fully functional programming language interpreter for the PyCombinator language. The interpreter will parse, evaluate, and execute user-input code, providing an interactive programming environment. It is implemented via command-line interaction, with core functionalities including lexical analysis, syntax analysis, expression evaluation, lambda function support, and a complete REPL environment. It is an educational project designed to help students understand the core concepts and implementation principles of programming language interpreters.

#### 2. Basic Functional Requirements

##### 2.1 Interactive Programming Environment (REPL)
- Provide a command-line interactive programming environment that allows users to input code and receive immediate execution results.
- Support launching the interactive environment with `python3 repl.py` and a read-only mode for debugging expression parsing with `python3 repl.py --read`.
- Offer friendly error messages and exception handling, allowing exit with Ctrl-C and Ctrl-D.
- Use a prompt-based main interface with `>` as the input prompt, supporting history and command-line editing (if available).

##### 2.2 Lexer
- Convert input strings into a sequence of tokens, supporting numeric literals (integers and floats), identifiers (variable names and function names), keywords (`lambda`), delimiters (`(`, `)`, `,`, `:`), and whitespace characters.
- Automatically skip whitespace, support negative numbers and decimals, and allow identifiers starting with underscores.
- Provide detailed syntax error messages, including error location and reason.

##### 2.3 Parser
- Convert the token sequence into an abstract syntax tree (AST), supporting literal expressions, name expressions, call expressions, and lambda expressions.
- Support nested parenthesis expressions, multi-parameter function calls, no-parameter lambda expressions, and immediately invoked lambda expressions.
- Display parsing status during execution, supporting interrupt operations (user can terminate parsing with Ctrl+C).

##### 2.4 Evaluator
- Execute the abstract syntax tree and return the computation result, supporting three value types: numeric values, lambda functions, and primitive functions.
- Support variable scopes, function closures, and environment copying and updating.
- Return evaluation status (success/failure), and in case of failure, provide specific reasons (e.g., type errors, undefined variables).

##### 2.5 Built-in Function Support
- Provide common mathematical operation functions: `add`, `sub`, `mul`, `truediv`, `floordiv`, `mod`, `pow`, `abs`, `max`, `min`, `int`, `float`.
- Support multi-parameter function calls, nested function calls, and recursive function calls.

##### 2.6 Lambda Expression Support
- Support anonymous function definition and invocation with the syntax: `lambda [parameter list]: expression`.
- Handle zero or more parameters, nested lambda expressions, higher-order functions (functions as parameters or return values), and closures (capturing external environment variables).

#### 3. Command-line Interaction and Result Display
- Use a prompt-based main interface with input validity checks, displaying messages in Chinese for invalid inputs.
- All output results should support formatted display, format error messages, and clearly indicate type mismatch issues in type errors.
- Support a debug mode to view the Python representation of expressions.