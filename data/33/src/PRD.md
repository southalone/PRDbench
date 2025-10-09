Federated Learning Training System PRD

1. Overview of Requirements

The system aims to provide machine learning researchers with a comprehensive federated learning experimental platform, supporting both offline and online federated learning modes. The system is implemented through command-line interaction, with core functionalities including offline federated learning training, online distributed training, parameter sweep experiment management, and training result recording and analysis. Users can conduct distributed model training while protecting data privacy and verify the effectiveness of different federated learning strategies.

2. Basic Functional Requirements

2.1 Offline Federated Learning Training Management

- Provide a command-line parameter configuration interface, supporting settings like the number of clients, training rounds, local training rounds, learning rate, and other hyperparameters.
- Support two training modes: full client participation mode (where all 20 clients participate in each round) and partial client participation mode (randomly selecting 5/10/15 clients).
- Display dynamic progress prompts during training (e.g., "Round 3/10, Client 5/20 training..."), supporting interrupt operations (users can terminate training by pressing Ctrl+C).
- Return training status (success/failure). In case of failure, provide specific reasons (e.g., data loading failure, model saving error, insufficient memory).
- Automatically save training logs, including test loss, accuracy per round, and best model save status.
- Data source supports pre-split MNIST datasets (pickle format), with each client having an independent data subset.

2.2 Online Federated Learning Distributed Training

- Implement server-client communication architecture based on TCP Socket, supporting concurrent connections from multiple clients.
- The server is responsible for global model initialization, parameter aggregation (FedAvg algorithm), and model distribution, while clients handle local model training.
- Support user-configured network parameters: receiving port, sending port, client count, training rounds, and local training rounds.
- Provide connection status monitoring, displaying client connection status (e.g., "Client 3 connected, 5/10 clients ready").
- Support visualization of the training process, showing aggregation progress and model performance metrics in real time.
- Automatically handle network anomalies, offering a retry mechanism for connection failures and error recovery functions.

2.3 Parameter Sweep Experiment Management

- Support batch execution of experiments with different parameter combinations, including client numbers (5/10/20), training rounds (10), and local training rounds (5/10).
- Provide a one-click execution script that automatically runs experiments with all parameter combinations.
- Experiment results are automatically categorized and stored, with each experiment generating an independent log file (e.g., "result_10_10_10.log").
- Support comparative analysis of experiments, allowing comparison of model performance under different parameter settings.
- Provide an experiment status query feature to display lists of ongoing and completed experiments.

2.4 Model Training and Evaluation

- Support training of MLP neural network architecture with input layer 784 dimensions (28×28 pixels), hidden layers 256→128 dimensions, and output layer 10 dimensions (MNIST classification).
- Provide model performance evaluation functionality, calculating accuracy, loss, and other metrics on a unified test set.
- Support model saving and loading, automatically saving the best performance model.
- Offer training process monitoring, recording loss changes and gradient information for each round.
- Support model visualization analysis, allowing viewing of model parameter distribution, gradient flow, etc.

3. Technical Specifications

3.1 System Architecture

- Programming Language: Python 3.x
- Deep Learning Framework: PyTorch
- Network Communication: Socket TCP/IP
- Data Processing: NumPy, TorchVision
- Logging System: Loguru

3.2 Model Configuration

- Network Type: Multilayer Perceptron (MLP)
- Optimizer: SGD (Stochastic Gradient Descent)
- Loss Function: Cross-Entropy Loss
- Activation Function: ReLU
- Batch Size: 32

3.3 Data Specifications

- Dataset: MNIST Handwritten Digit Dataset
- Data Format: Pre-split pickle files
- Number of Clients: 20 independent data subsets
- Test Set: Unified MNIST test set

4. Command-Line Interaction and Result Presentation

4.1 Main Interface Interaction

- The main interface uses a menu-style interaction with function options: [1] Offline Federated Learning [2] Online Federated Learning [3] Parameter Sweep Experiment [4] View Training Logs [5] Model Evaluation [6] Exit.
- User input is subject to validity checks (e.g., options must be numbers 1-6, parameter values must be within a reasonable range), displaying error prompts in Chinese for invalid input.
- Support parameter configuration wizards to guide users in setting training parameters.

4.2 Result Presentation

- When generating analysis results, users can choose whether to display training metrics in a tabular text format.
- Support visualization of the training process, displaying plots of loss curves, accuracy changes, etc.
- All output results can be saved as TXT files (users can specify the save path), and files should include training parameters, performance metrics, model information, and tabular text.

4.3 Log Management

- Automatically generate training log files that include timestamps, training parameters, and performance metrics.
- Support log query features, allowing filtering of historical records by time and parameter combinations.
- Provide log analysis tools for batch log processing and result summarization.