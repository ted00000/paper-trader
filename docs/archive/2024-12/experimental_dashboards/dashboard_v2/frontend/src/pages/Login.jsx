import { useState } from 'react'
import { motion } from 'framer-motion'
import { Lock, User, AlertCircle, Eye, EyeOff } from 'lucide-react'

function Login({ onLogin }) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const response = await fetch('/api/v2/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
      })

      const data = await response.json()

      if (response.ok) {
        // Store session token
        localStorage.setItem('tedbot_session', data.token)
        onLogin(data.token, data.is_super_user)
      } else {
        setError(data.error || 'Invalid credentials')
      }
    } catch (err) {
      setError('Connection error. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-tedbot-dark flex items-center justify-center p-6">
      {/* Background gradient effects */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-tedbot-accent opacity-5 rounded-full blur-3xl"></div>
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-profit opacity-5 rounded-full blur-3xl"></div>
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="relative w-full max-w-md"
      >
        {/* Login Card */}
        <div className="glass rounded-2xl p-8 border-2 border-tedbot-gray-800">
          {/* Logo and Header */}
          <div className="text-center mb-8">
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ delay: 0.2, duration: 0.5 }}
              className="flex justify-center mb-4"
            >
              <img
                src="/tedbot-logo.png"
                alt="Tedbot Logo"
                className="w-20 h-20 rounded-xl"
              />
            </motion.div>
            <motion.h1
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.3, duration: 0.5 }}
              className="text-4xl font-bold gradient-text mb-2"
            >
              Tedbot
            </motion.h1>
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.4, duration: 0.5 }}
              className="text-tedbot-gray-500"
            >
              Autonomous Trading Terminal
            </motion.p>
          </div>

          {/* Login Form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Error Message */}
            {error && (
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                className="bg-loss bg-opacity-10 border border-loss rounded-lg p-4 flex items-center gap-3"
              >
                <AlertCircle className="text-loss flex-shrink-0" size={20} />
                <p className="text-loss text-sm">{error}</p>
              </motion.div>
            )}

            {/* Username Field */}
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-tedbot-gray-400 mb-2">
                Username
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <User className="text-tedbot-gray-600" size={20} />
                </div>
                <input
                  id="username"
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full bg-tedbot-darker border border-tedbot-gray-800 rounded-lg pl-10 pr-4 py-3 text-white placeholder-tedbot-gray-600 focus:outline-none focus:border-tedbot-accent transition-colors"
                  placeholder="Enter username"
                  required
                  autoComplete="username"
                  autoFocus
                />
              </div>
            </div>

            {/* Password Field */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-tedbot-gray-400 mb-2">
                Password
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Lock className="text-tedbot-gray-600" size={20} />
                </div>
                <input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full bg-tedbot-darker border border-tedbot-gray-800 rounded-lg pl-10 pr-12 py-3 text-white placeholder-tedbot-gray-600 focus:outline-none focus:border-tedbot-accent transition-colors"
                  placeholder="Enter password"
                  required
                  autoComplete="current-password"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center text-tedbot-gray-600 hover:text-tedbot-accent transition-colors"
                >
                  {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                </button>
              </div>
            </div>

            {/* Submit Button */}
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-tedbot-accent to-profit font-semibold py-3 rounded-lg hover:shadow-lg hover:shadow-tedbot-accent/20 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <div className="flex items-center justify-center gap-2">
                  <div className="w-5 h-5 border-2 border-tedbot-darker border-t-transparent rounded-full animate-spin"></div>
                  <span className="text-tedbot-darker">Signing in...</span>
                </div>
              ) : (
                <span className="text-tedbot-darker">Sign In</span>
              )}
            </motion.button>
          </form>

          {/* Footer */}
          <div className="mt-8 pt-6 border-t border-tedbot-gray-800">
            <p className="text-center text-xs text-tedbot-gray-600">
              Secure access to your autonomous trading dashboard
            </p>
          </div>
        </div>

        {/* Security Notice */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6, duration: 0.5 }}
          className="mt-6 text-center"
        >
          <p className="text-xs text-tedbot-gray-600 flex items-center justify-center gap-2">
            <Lock size={14} />
            <span>Protected by end-to-end encryption</span>
          </p>
        </motion.div>
      </motion.div>
    </div>
  )
}

export default Login
