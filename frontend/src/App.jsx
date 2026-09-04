import {
  Navigate,
  Route,
  Routes,
} from 'react-router'

import { ProtectedRoute } from './components/routing/ProtectedRoute'
import { RoleRoute } from './components/routing/RoleRoute'

function PlaceholderPage ({ title, description }) {
  return (
    <main>
      <p>Streamline</p>
      <h1>{title}</h1>
      <p>{description}</p>  
    </main>
  )
}