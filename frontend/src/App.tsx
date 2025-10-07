import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import Playground from './pages/Playground';
import Gallery from './pages/Gallery';
import Settings from './pages/Settings';
import { Button } from './components/ui/button';

function Navigation() {
  const location = useLocation();

  const isActive = (path: string) => location.pathname === path;

  return (
    <nav className="border-b">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center gap-8">
            <Link to="/" className="text-xl font-bold">
              MediaRouter
            </Link>
            <div className="flex gap-1">
              <Link to="/">
                <Button
                  variant={isActive('/') ? 'default' : 'ghost'}
                  size="sm"
                >
                  Playground
                </Button>
              </Link>
              <Link to="/gallery">
                <Button
                  variant={isActive('/gallery') ? 'default' : 'ghost'}
                  size="sm"
                >
                  Gallery
                </Button>
              </Link>
              <Link to="/settings">
                <Button
                  variant={isActive('/settings') ? 'default' : 'ghost'}
                  size="sm"
                >
                  Settings
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
}

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-background">
        <Navigation />
        <Routes>
          <Route path="/" element={<Playground />} />
          <Route path="/gallery" element={<Gallery />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
