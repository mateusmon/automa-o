import {useState} from 'react'

const TESTS = [
  { id: 1, name: "Entrada Simples" },
  { id: 2, name: "Cadastro de Requiisção"},
  { id: 3, name: "Atendimento de Requisição"},
  { id: 4, name: "Devolução de Materiais"},
  { id: 5, name: "Baixa de Material"}
]

function TestSelector({ tests }) {
  const [selected, setSelected] = useState([])
  
  function handleChange(testId) {
    if (selected.includes(testId)) {
      setSelected(selected.filter(id => id !== testId))
    } else {
      setSelected([...selected, testId])
    }
  }

  function handleRun() {
    const selectedNames = tests
      .filter(test => selected.includes(test.id))
      .map(test => test.name)
    
      console.log(selectedNames)
  }

  return (
    <div>
      {tests.map(test => (
        <div key={test.id}>
          <label>
            <input 
              type="checkbox"
              checked={selected.includes(test.id)}
              onChange={() => handleChange(test.id)}
            />
            {test.name}
          </label>
        </div>
      ))}

      <p>{selected.length} tests selected</p>
      <button onClick={handleRun}>Logar Nomes</button>
    </div>
  )
}

function App() {
  return <div className="text-red-500">Hello!</div>
  //<TestSelector tests={TESTS}/>
}

export default App