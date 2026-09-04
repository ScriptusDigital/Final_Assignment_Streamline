import {
  Navigate,
  Route,
  Routes,
} from 'react-router'
import { AppShell } from './components/layout/AppShell'
import { ProtectedRoute } from './components/routing/ProtectedRoute'
import { RoleRoute } from './components/routing/RoleRoute'
import { LoginPage } from './pages/LoginPage'

function PlaceholderPage ({ title, description }) {
  return (
<section>
      <p>Streamline</p>
      <h1>{title}</h1>
      <p>{description}</p>  
</section>
  )
}


export default function App() {
  return (
    <Routes>
      <Route
        path="/"
        element={
          <PlaceholderPage
            title="Digital asset management"
            description="Organise, review and securely distribute photography."
          />
        }
      />
    
<Route
  path="/login"
  element={<LoginPage />}
/>

<Route
        path="/register"
        element={
          <PlaceholderPage
            title="Create an account"
            description="Register as a Streamline viewer."
          />
        }
      />

    <Route element={<ProtectedRoute />}>
<Route element={<AppShell />}>
        <Route
          path="/dashboard"
          element={
            <PlaceholderPage
              title="Dashboard"
              description="An overview of your assets and workflow."
            />
          }
        />

        <Route
          path="/library"
          element={
            <PlaceholderPage
              title="Asset library"
              description="Search and filter approved photography."
            />
          }
        />

        <Route
          path="/assets/:assetId"
          element={
            <PlaceholderPage
              title="Asset details"
              description="Review metadata, rights and asset history."
            />
          }
        />

        <Route
          path="/collections"
          element={
            <PlaceholderPage
              title="Collections"
              description="Browse related groups of assets."
            />
          }
        />

        <Route
          path="/profile"
          element={
            <PlaceholderPage
              title="Profile"
              description="View your Streamline account."
            />
          }
        />

        <Route
          element={
            <RoleRoute
              allowedRoles={['editor', 'admin']}
            />
          }
        >
          <Route
            path="/upload"
            element={
              <PlaceholderPage
                title="Upload"
                description="Upload and describe a new asset."
              />
            }
          />
        </Route>

        <Route
          element={
            <RoleRoute
              allowedRoles={['admin']}
            />
          }
        >
          <Route
            path="/review"
            element={
              <PlaceholderPage
                title="Review queue"
                description="Approve assets or request changes."
              />
            }
          />
        </Route>
      </Route>
</Route>

      <Route
        path="/home"
        element={
          <Navigate
            to="/dashboard"
            replace
          />
        }
      />

      <Route
        path="*"
        element={
          <PlaceholderPage
            title="Page not found"
            description="The requested page does not exist."
          />
        }
      />
    </Routes>
  )
}