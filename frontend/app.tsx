import { useState } from 'react'

function App() {
    const [count, setCount] = useState(0)

    return (
        <>
            <section className="container mx-auto mt-4">
                <div>
                    <h1>Test Vite</h1>
                </div>
                <button
                    className="counter bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
                    onClick={() => setCount((count) => count + 1)}
                >
                    Count is {count}
                </button>
            </section>
        </>
    )
}

export default App
