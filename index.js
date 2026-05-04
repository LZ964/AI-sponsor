import { task } from '@renderinc/sdk/workflows'

const calculateSquare = task(
  { name: 'calculateSquare' },
  function calculateSquare(a: number): number {
    return a * a
  }
)
