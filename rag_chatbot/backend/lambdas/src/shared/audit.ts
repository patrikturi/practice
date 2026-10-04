export function audit(eventName: string, fields: Record<string, unknown> = {}): void {
  console.log(
    JSON.stringify({
      type: 'audit',
      event: eventName,
      ts: new Date().toISOString(),
      ...fields,
    })
  );
}
