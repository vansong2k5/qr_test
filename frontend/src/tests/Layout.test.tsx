import { describe, it, expect } from 'vitest'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import { render, screen } from '@testing-library/react'
import Layout from '../components/Layout'

const Dummy = () => <div>Content</div>

describe('Layout', () => {
  it('renders navigation', () => {
    render(
      <MemoryRouter initialEntries={['/']}>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<Dummy />} />
          </Route>
        </Routes>
      </MemoryRouter>
    )
    expect(screen.getByText(/Dashboard/i)).toBeInTheDocument()
  })
})
