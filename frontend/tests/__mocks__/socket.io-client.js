export const io = vi.fn(() => ({
  on: vi.fn(),
  disconnect: vi.fn(),
  emit: vi.fn()
}))