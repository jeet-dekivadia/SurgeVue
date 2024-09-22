import SwiftUI
import FirebaseDatabase
import FirebaseDatabaseSwift

struct Patient: View {
    @State private var accelerationAlert: Bool = false
    @State private var showPatientInfo = false
    @State private var showShakyHandAlert = false
    @State private var unstableDetections: [String] = []
    @State private var isClockedIn: Bool = false
    @State private var showNotification: Bool = false

    var body: some View {
        ZStack {
            Color(red: 0.4, green: 0.8, blue: 0.8)
                .ignoresSafeArea()

            VStack(spacing: 20) {
                Button(action: {
                    showPatientInfo = true
                }) {
                    ProfilePictureView()
                }
                .padding(.top, -20)

                SensorDataView(accelerationAlert: accelerationAlert, showShakyHandAlert: $showShakyHandAlert)
                    .padding()
                    .background(Color(red: 0.9, green: 0.9, blue: 0.9))
                    .cornerRadius(20)
                    .shadow(radius: 5)

                UnstableDetectionLogView(log: unstableDetections)
                    .padding()
                    .background(Color(red: 0.9, green: 0.9, blue: 0.9))
                    .cornerRadius(20)
                    .shadow(radius: 5)

                HStack(spacing: 20) {
                    Button(action: clockIn) {
                        Text("Clock In")
                            .padding()
                            .background(Color.green)
                            .foregroundColor(.white)
                            .cornerRadius(10)
                    }
                    .disabled(isClockedIn)

                    Button(action: clockOut) {
                        Text("Clock Out")
                            .padding()
                            .background(Color.red)
                            .foregroundColor(.white)
                            .cornerRadius(10)
                    }
                    .disabled(!isClockedIn)
                }
            }
            .padding()
            .sheet(isPresented: $showPatientInfo) {
                PatientInfoView()
            }
            .alert(isPresented: $showShakyHandAlert) {
                Alert(
                    title: Text("Surgeon's Hand Shakiness Detected"),
                    message: Text("Unusual movement detected in surgeon's hand."),
                    dismissButton: .default(Text("OK"))
                )
            }
            .overlay(
                NotificationView(isPresented: $showNotification)
            )
        }
        .onAppear {
            fetchAccelerationAlertData()
        }
    }

    private func fetchAccelerationAlertData() {
        let ref = Database.database().reference()

        ref.child("motionData/accelerationAlert").observe(.value, with: { snapshot in
            if let value = snapshot.value as? Bool {
                accelerationAlert = value
                if value && isClockedIn {
                    showShakyHandAlert = true
                    let timestamp = Date().formatted(date: .abbreviated, time: .standard)
                    unstableDetections.append("\(timestamp): Hand Unstable")
                }
            }
        })
    }

    private func clockIn() {
        isClockedIn = true
        unstableDetections.removeAll()
    }

    private func clockOut() {
        isClockedIn = false
        showNotification = true
        // Here you would typically send the log data to your AI system and database
        // For this example, we'll just clear the logs after a delay
        DispatchQueue.main.asyncAfter(deadline: .now() + 3) {
            unstableDetections.removeAll()
            showNotification = false
        }
    }
}

struct SensorDataView: View {
    let accelerationAlert: Bool
    @Binding var showShakyHandAlert: Bool

    var body: some View {
        VStack(spacing: 20) {
            Text("Sensor Data")
                .font(.title)
                .fontWeight(.bold)
                .foregroundColor(Color(red: 0.2, green: 0.2, blue: 0.2))

            HStack {
                Text("Hand Stability:")
                    .font(.headline)
                    .foregroundColor(Color(red: 0.4, green: 0.4, blue: 0.4))
                
                Text(accelerationAlert ? "Unstable" : "Stable")
                    .font(.subheadline)
                    .foregroundColor(accelerationAlert ? .red : .green)
            }
        }
        .padding()
    }
}

struct UnstableDetectionLogView: View {
    let log: [String]

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text("Unstable Detection Log")
                .font(.headline)
                .foregroundColor(Color(red: 0.2, green: 0.2, blue: 0.2))

            if log.isEmpty {
                Text("No unstable detections recorded")
                    .font(.subheadline)
                    .foregroundColor(Color(red: 0.4, green: 0.4, blue: 0.4))
            } else {
                ScrollView {
                    ForEach(log, id: \.self) { entry in
                        Text(entry)
                            .font(.subheadline)
                            .foregroundColor(Color(red: 0.4, green: 0.4, blue: 0.4))
                    }
                }
            }
        }
        .frame(maxHeight: 150) // Limit initial height, will expand as needed
    }
}

struct ProfilePictureView: View {
    var body: some View {
        Image(systemName: "person.circle.fill")
            .resizable()
            .aspectRatio(contentMode: .fit)
            .frame(width: 120, height: 120)
            .foregroundColor(Color(red: 0.3, green: 0.6, blue: 1))
            .padding()
            .background(Color(red: 0.2, green: 0.5, blue: 0.8))
            .cornerRadius(80)
            .overlay(
                Circle()
                    .stroke(Color.white, lineWidth: 4)
            )
    }
}

struct PatientInfoView: View {
    var body: some View {
        VStack(spacing: 20) {
            Text("Patient Information")
                .font(.title)
                .fontWeight(.bold)
                .foregroundColor(Color(red: 0.2, green: 0.2, blue: 0.2))

            VStack(alignment: .leading, spacing: 10) {
                Text("Name: John Doe")
                    .font(.headline)
                Text("Address: 123 Main Street, Anytown USA")
                    .font(.subheadline)
                Text("Weight: 75 kg")
                    .font(.subheadline)
                Text("Emergency Contacts:")
                    .font(.headline)
                Text("Jane Doe (Wife) - 555-1234")
                    .font(.subheadline)
                Text("Dr. Smith (Physician) - 555-5678")
                    .font(.subheadline)
            }
            .padding()
            .background(Color(red: 0.9, green: 0.9, blue: 0.9))
            .cornerRadius(20)
            .shadow(radius: 5)

            VStack(alignment: .leading, spacing: 10) {
                Text("Medications:")
                    .font(.headline)
                Text("- Aspirin (81mg) - Once daily")
                    .font(.subheadline)
                Text("- Lisinopril (10mg) - Once daily")
                    .font(.subheadline)
                Text("Upcoming Appointments:")
                    .font(.headline)
                Text("- Physical Exam - June 15, 2023")
                    .font(.subheadline)
                Text("- Cardiology Follow-up - July 1, 2023")
                    .font(.subheadline)
            }
            .padding()
            .background(Color(red: 0.9, green: 0.9, blue: 0.9))
            .cornerRadius(20)
            .shadow(radius: 5)

            Spacer()
        }
        .padding()
        .background(Color(red: 0.95, green: 0.95, blue: 0.95))
    }
}

struct NotificationView: View {
    @Binding var isPresented: Bool

    var body: some View {
        if isPresented {
            VStack {
                Text("Log sent to AI for evaluation")
                    .padding()
                    .background(Color.blue)
                    .foregroundColor(.white)
                    .cornerRadius(10)
            }
            .transition(.move(edge: .top))
        }
    }
}
