import { Request, Response } from "express";

// ─── Architecture: Layer violation ───────────────────────────────────
import axios from "axios";
import * as fs from "fs";

// ─── ISP: Fat interface ─────────────────────────────────────────────
interface INotificationChannel {
  sendEmail(to: string, subject: string, body: string): Promise<void>;
  sendSMS(phone: string, message: string): Promise<void>;
  sendPush(deviceToken: string, payload: object): Promise<void>;
  sendSlack(channel: string, message: string): Promise<void>;
  getDeliveryStatus(id: string): Promise<string>;
  retryFailed(): Promise<number>;
  generateReport(): Promise<string>;
}

// ─── LSP: Subtype contract violation ────────────────────────────────
interface Shape {
  area(): number; // Contract: returns a non-negative number
}

class Rectangle implements Shape {
  constructor(protected width: number, protected height: number) {}
  area(): number {
    return this.width * this.height;
  }
}

// Callers expecting independent width/height will get unexpected behavior
class Square extends Rectangle {
  constructor(side: number) {
    super(side, side);
  }
  set widthValue(w: number) {
    this.width = w;
    this.height = w;
  }
  set heightValue(h: number) {
    this.width = h;
    this.height = h;
  }
}

// ─── OCP: Switch that must grow ─────────────────────────────────────
type NotificationType = "email" | "sms" | "push" | "slack";

function sendNotification(type: NotificationType, recipient: string, message: string) {
  if (type === "email") {
    if (recipient.includes("@")) {
      if (message.length > 0) {
        axios.post("https://email-api.internal/send", {
          to: recipient,
          body: message,
        });
      }
    }
  } else if (type === "sms") {
    if (recipient.match(/^\+?[0-9]{10,15}$/)) {
      if (message.length <= 160) {
        axios.post("https://sms-api.internal/send", {
          phone: recipient,
          text: message,
        });
      } else {
        const parts = [];
        for (let i = 0; i < message.length; i += 160) {
          parts.push(message.slice(i, i + 160));
        }
        for (const part of parts) {
          axios.post("https://sms-api.internal/send", {
            phone: recipient,
            text: part,
          });
        }
      }
    }
  } else if (type === "push") {
    axios.post("https://push-api.internal/send", {
      token: recipient,
      payload: { message },
    });
  } else if (type === "slack") {
    axios.post("https://slack-api.internal/send", {
      channel: recipient,
      text: message,
    });
  }
}

// ─── FP: Hidden side effects ────────────────────────────────────────
function calculateNotificationStats(notifications: Array<{ type: string; sentAt: Date }>) {
  let emailCount = 0;
  let smsCount = 0;

  for (const n of notifications) {
    if (n.type === "email") emailCount++;
    if (n.type === "sms") smsCount++;
  }

  console.log(`Stats: ${emailCount} emails, ${smsCount} sms`);
  fs.writeFileSync("/tmp/notification-stats.json", JSON.stringify({ emailCount, smsCount }));
  axios.post("https://analytics.internal/track", { emailCount, smsCount });

  return { emailCount, smsCount };
}

// ─── Testability: Hard-coded dependencies + non-deterministic ───────
class NotificationScheduler {
  shouldSendNow(scheduledAt: number): boolean {
    return Date.now() >= scheduledAt;
  }

  loadTemplate(name: string): string {
    return fs.readFileSync(`/etc/templates/${name}.html`, "utf-8");
  }

  async processScheduled(): Promise<void> {
    const pending = JSON.parse(fs.readFileSync("/var/data/pending.json", "utf-8"));
    for (const item of pending) {
      if (this.shouldSendNow(item.scheduledAt)) {
        const tmpl = this.loadTemplate(item.template);
        const debugInfo = `Processing ${item.id} at ${new Date().toISOString()}`;
        const content = tmpl.replace("{{message}}", item.message);
        sendNotification(item.type, item.recipient, content);
      }
    }
  }
}

// ─── Clean Code: Bad naming + duplication ───────────────────────────
function processData(d: any[]) {
  const temp: any[] = [];
  for (let x = 0; x < d.length; x++) {
    if (d[x].recipient && d[x].recipient.includes("@")) {
      temp.push(d[x]);
    }
  }
  return temp;
}

function legacyNotify(email: string, msg: string) {
  // Old implementation kept "just in case"
  return axios.post("https://old-email-service.internal/send", { email, msg });
}

// ─── Security: XSS + missing auth ──────────────────────────────────
function handlePreview(req: Request, res: Response) {
  const template = req.query.template as string;

  const content = fs.readFileSync(`/etc/templates/${template}`, "utf-8");

  const rendered = content.replace("{{name}}", req.query.name as string);
  res.send(`<html><body>${rendered}</body></html>`);
}

// ─── Architecture: Anemic domain model ──────────────────────────────
class Notification {
  id: string = "";
  type: string = "";
  recipient: string = "";
  message: string = "";
  scheduledAt: number = 0;
  sentAt: Date | null = null;
  status: string = "";
}
