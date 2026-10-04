// Package worker drains the outbound notification queue.
package worker

// Drain forwards queued messages to send until queue or done is closed.
func Drain(queue <-chan string, done <-chan struct{}, send func(string)) {
	for {
		select {
		case msg, ok := <-queue:
			if !ok {
				return
			}
			send(msg)
		case <-done:
			return
		default:
		}
	}
}
