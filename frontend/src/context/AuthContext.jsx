import { createContext, useContext, useState, useEffect } from 'react'
import { API_URL as API } from '../config';

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
    const [user, setUser] = useState(null)
    const [token, setToken] = useState(null)
    const [loading, setLoading] = useState(true)

    // Load saved auth on app start
    useEffect(() => {
        const savedToken = localStorage.getItem('af_token')
        const savedUser = localStorage.getItem('af_user')
        if (savedToken && savedUser) {
            try {
                setToken(savedToken)
                setUser(JSON.parse(savedUser))
            } catch { }
        }
        setLoading(false)
    }, [])

    const login = (tokenStr, userObj) => {
        setToken(tokenStr)
        setUser(userObj)
        localStorage.setItem('af_token', tokenStr)
        localStorage.setItem('af_user', JSON.stringify(userObj))
    }

    const logout = () => {
        setToken(null)
        setUser(null)
        localStorage.removeItem('af_token')
        localStorage.removeItem('af_user')
    }

    const authFetch = (url, options = {}) => {
        return fetch(url, {
            ...options,
            headers: {
                ...(options.headers || {}),
                ...(token ? { Authorization: `Bearer ${token}` } : {}),
                ...(options.body && !(options.body instanceof FormData) ? { 'Content-Type': 'application/json' } : {}),
            },
        })
    }

    return (
        <AuthContext.Provider value={{ user, token, login, logout, authFetch, loading, isAdmin: user?.role === 'admin' }}>
            {children}
        </AuthContext.Provider>
    )
}

export const useAuth = () => useContext(AuthContext)
