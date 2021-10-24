import torch


# class LSTM(torch.nn.Module):
#
#     def __init__(self, num_classes, input_size, hidden_size, num_layers, seq_length):
#         super(LSTM, self).__init__()
#
#         self.num_classes = num_classes
#         self.num_layers = num_layers
#         self.input_size = input_size
#         self.hidden_size = hidden_size
#         self.seq_length = seq_length
#
#         self.lstm = torch.nn.LSTM(input_size=input_size, hidden_size=hidden_size,
#                             num_layers=num_layers, batch_first=True)
#
#         self.fc = torch.nn.Linear(hidden_size, num_classes)
#
#     def forward(self, x):
#         h_0 = torch.zeros(
#             self.num_layers, x.size(0), self.hidden_size).cuda()
#
#         c_0 = torch.zeros(
#             self.num_layers, x.size(0), self.hidden_size).cuda()
#
#         # Propagate input through LSTM
#         ula, (h_out, _) = self.lstm(x, (h_0, c_0))
#         # output, status = self.lstm(x) # batchXD
#         # output = output[:,-1,:]
#
#         h_out = h_out.view(-1, self.hidden_size)
#
#         out = self.fc(h_out)
#         # out = self.fc(output)
#
#         return out


class LSTM(torch.nn.Module):
    def __init__(self, input_size=1, hidden_layer_size=100, output_size=1, num_layers=1):
        super().__init__()
        self.hidden_layer_size = hidden_layer_size

        self.lstm = torch.nn.LSTM(input_size, hidden_layer_size, batch_first=True)

        self.linear = torch.nn.Linear(hidden_layer_size*10, output_size)

        self.num_layers = num_layers

        # self.hidden_cell = (torch.zeros(1,1,self.hidden_layer_size),
        #                     torch.zeros(1,1,self.hidden_layer_size))

    def forward(self, input_seq):
        h_0 = torch.zeros(
            self.num_layers, input_seq.size(0), self.hidden_layer_size).cuda()

        c_0 = torch.zeros(
            self.num_layers, input_seq.size(0), self.hidden_layer_size).cuda()

        # lstm_out, self.hidden_cell = self.lstm(input_seq, self.hidden_cell)
        lstm_out, self.hidden_cell = self.lstm(input_seq, (h_0, c_0))
        predictions = self.linear(lstm_out.reshape(len(input_seq), -1))
        return predictions #[-1]



X = torch.load('kitti_car_train_x_10_normalize_pos.pt')
Y = torch.load('kitti_car_train_label_10_normalize_pos.pt')

test_X = torch.load('kitti_car_test_x_10_normalize_pos.pt')
test_Y = torch.load('kitti_car_test_label_10_normalize_pos.pt')



train_size = int(X.size()[0] * 0.95)
test_size = X.size()[0] - train_size

trainX = X[0:train_size].float().cuda()
trainY = Y[0:train_size].float().cuda()

valX = X[train_size:].float().cuda()
valY = Y[train_size:].float().cuda()

testX = test_X.float().cuda()
testY = test_Y.float().cuda()

num_epochs = 8000 #10000
learning_rate = 0.001

input_size = 3
hidden_size = 50
output_size = 3

# lstm = LSTM(num_classes, input_size, hidden_size, num_layers, seq_length)
lstm = LSTM(input_size=hidden_size, hidden_layer_size=hidden_size, output_size=output_size)
lstm = lstm.cuda()
lstm.train()

criterion = torch.nn.MSELoss()  # mean-squared error for regression
optimizer = torch.optim.Adam(lstm.parameters(), lr=learning_rate)
# optimizer_scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=5000, gamma=0.5)
# optimizer = torch.optim.SGD(lstm.parameters(), lr=learning_rate)

# Train the model
for epoch in range(num_epochs):
    # optimizer_scheduler.step()

    outputs = lstm(trainX)
    optimizer.zero_grad()

    # obtain the loss function
    loss = criterion(outputs.unsqueeze(1), trainY)

    loss.backward()

    optimizer.step()
    if epoch % 100 == 0:
        # validation
        lstm = lstm.eval()
        predictions = lstm(valX)
        val_loss = criterion(predictions.unsqueeze(1), valY)
        # testing
        test_predictions = lstm(testX)
        test_loss = criterion(test_predictions.unsqueeze(1), testY)
        print("Epoch: %d, training loss: %1.5f val loss: %1.5f test loss: %1.5f" % (epoch, loss.item(), val_loss.item(), test_loss.item()))

        lstm = lstm.train()
torch.save(lstm.state_dict(), './BAT/lstm_models/car_model_normalize_position_'+str(epoch)+'.pt')
