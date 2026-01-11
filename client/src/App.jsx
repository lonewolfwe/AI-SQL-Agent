import { useState, useRef, useEffect } from 'react'
import './App.css'

function App() {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Hello! I am your AI SQL Agent. Ask me anything about your data.' }
  ])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!input.trim()) return

    const userMessage = input
    setInput('')
    setMessages(prev => [...prev, { role: 'user', content: userMessage }])
    setIsLoading(true)

    try {
      const response = await fetch('http://localhost:5000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: userMessage }),
      })

      const data = await response.json()
      
      if (data.error) {
        setMessages(prev => [...prev, { role: 'assistant', content: `Error: ${data.error}`, isError: true }])
      } else {
        setMessages(prev => [...prev, { 
          role: 'assistant', 
          content: data.answer,
          sql: data.sql,
          result: data.result
        }])
      }
    } catch (error) {
      setMessages(prev => [...prev, { role: 'assistant', content: `Network Error: ${error.message}`, isError: true }])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>📊 AI SQL Agent</h1>
      </header>
      
      <div className="chat-container">
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.role} ${msg.isError ? 'error' : ''}`}>
            <div className="message-content">
              <p>{msg.content}</p>
              
              {msg.sql && (
                <div className="sql-block">
                  <div className="sql-header">Generated SQL</div>
                  <pre><code>{msg.sql}</code></pre>
                </div>
              )}
              
              {msg.result && (
                <div className="result-block">
                  <div className="result-header">Raw Result</div>
                  <pre>{msg.result}</pre>
                </div>
              )}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="message assistant loading">
            <div className="typing-indicator">
              <span></span><span></span><span></span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <form className="input-area" onSubmit={handleSubmit}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question (e.g., 'How many tracks are there?')"
          disabled={isLoading}
        />
        <button type="submit" disabled={isLoading || !input.trim()}>
          Send
        </button>
      </form>
    </div>
  )
}

export default App
