# Program Manipulation with AST

## Code Mutation
The program 1.py does the following basic code mutations:

- Negate Binary Operators: + $\Leftrightarrow$ -, * $\Leftrightarrow$ /
- Negate Comparision Operators: >= $\Leftrightarrow$ <, <= $\Leftrightarrow$ >
- Delete Unused Function Definitions

In addition to that, all global variables are displayed one by one at the end of the program. Note that functions such as find() and replace() are not used in the implementation. Only functions in AST are used.

## Undefined Variables Identification
An undefined variable is a variable that is accessed in the code but has not been declared by that code Static undefined variable identification (without running the program) is very useful and has already been applied in many applications. For example, the Python extension in Visual Studio Code marks the undefined variables before the program is actually run. However, debugging can be very time-consuming without undefined variable identification. Let’s say when you are doing a homework, you have written a Python code to perform some heavy computations and save the final result to a file. Let’s further assume there is only two hours left to ddl, and the program takes an hour and a half to finish. Unluckily, you accidentally introduced an undefined variable somewhere before the saving operation. Once you click the run button, you will certainly miss the ddl.

The program 2.py counts the number of uses of undefined variables given a program.
