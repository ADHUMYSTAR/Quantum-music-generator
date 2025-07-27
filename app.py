from flask import Flask, request, jsonify
from qiskit import QuantumCircuit, Aer, transpile, assemble
from qiskit.visualization import plot_histogram
from music21 import stream, note, midi
import base64
import io

app = Flask(__name__)

# Map binary strings to musical notes
NOTE_MAP = {
    '000': 'C4', '001': 'D4', '010': 'E4', '011': 'F4',
    '100': 'G4', '101': 'A4', '110': 'B4', '111': 'C5'
}

def quantum_music_generator(emotion):
    num_qubits = 3
    shots = 16  # melody length

    qc = QuantumCircuit(num_qubits, num_qubits)

    if emotion == 'happy':
        # Use Hadamard to create superposition
        for q in range(num_qubits):
            qc.h(q)
    elif emotion == 'sad':
        # Initialize some qubits to |1⟩
        qc.x(0)
    elif emotion == 'calm':
        qc.h(1)
    else:
        # default mixed emotions
        qc.h(0)
        qc.x(2)

    # Measure
    qc.measure(range(num_qubits), range(num_qubits))

    simulator = Aer.get_backend('qasm_simulator')
    transpiled = transpile(qc, simulator)
    qobj = assemble(transpiled, shots=shots)
    result = simulator.run(qobj).result()
    counts = result.get_counts()

    # Flatten output into notes
    melody = []
    for outcome in counts:
        note_name = NOTE_MAP.get(outcome[-3:], 'C4')  # last 3 bits
        melody.extend([note_name] * counts[outcome])

    return melody[:16]  # return 16 notes

def create_midi_stream(melody):
    s = stream.Stream()
    for pitch in melody:
        n = note.Note(pitch)
        n.quarterLength = 0.5
        s.append(n)

    # Convert to MIDI binary
    mf = midi.translate.streamToMidiFile(s)
    midi_io = io.BytesIO()
    mf.writeFile(midi_io)
    midi_io.seek(0)

    return base64.b64encode(midi_io.read()).decode()

@app.route('/generate_music', methods=['POST'])
def generate_music():
    data = request.get_json()
    emotion = data.get('emotion', 'happy')

    melody = quantum_music_generator(emotion)
    midi_data = create_midi_stream(melody)

    return jsonify({
        'melody': melody,
        'midi_base64': midi_data,
        'message': f"Quantum music generated for '{emotion}' emotion"
    })

if __name__ == '__main__':
    app.run(debug=True)
