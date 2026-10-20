let tail: Promise<unknown> = Promise.resolve()

/** Run heavy API calls one at a time so the single NAS worker is not flooded. */
export function enqueue<T>(task: () => Promise<T>): Promise<T> {
  const run = tail.then(task, task)
  tail = run.then(
    () => undefined,
    () => undefined,
  )
  return run
}
