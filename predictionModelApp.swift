import SwiftUI
import Combine

struct PredictionView: View {
    @State private var userInput: String = ""
    @State private var chatHistory: [String] = []

    var body: some View {
        VStack {
            ScrollView {
                LazyVStack(alignment: .leading, spacing: 8) {
                    ForEach(chatHistory, id: \.self) { message in
                        Text(message)
                            .padding(8)
                            .background(Color.gray.opacity(0.2))
                            .cornerRadius(8)
                    }
                }
            }
            HStack {
                TextField("Type your message...", text: $userInput)
                    .textFieldStyle(RoundedBorderTextFieldStyle())
                Button(action: sendMessage) {
                    Text("Send")
                }
            }
            .padding()
        }
        .padding()
    }

    func sendMessage() {
        guard !userInput.isEmpty else { return }

        // Add user's message to chat history
        chatHistory.append("User: \(userInput)")

        // Simulate API call and add response to chat history
        getOpenAIResponse { response in
            DispatchQueue.main.async {
                // Add response to chat history
                chatHistory.append("ChatGPT: \(response)")

                // Clear user input
                userInput = ""
            }
        }
    }

    func getOpenAIResponse(completion: @escaping (String) -> Void) {
        let response = "Based on analysis on previous Data, your hand stability scores 97.0 % and the patient has bled out 0 times."

        // Delay the completion handler by 3 seconds
        DispatchQueue.main.asyncAfter(deadline: .now() + 3) {
            completion(response)
        }
    }
}

struct PredictionView_Previews: PreviewProvider {
    static var previews: some View {
        PredictionView()
    }
}
