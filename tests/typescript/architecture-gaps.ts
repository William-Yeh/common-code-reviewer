import { cyclePeer } from "./cycle-peer";
import express from "express";
import cors from "cors";
import serialize from "node-serialize";
import fs from "node:fs";

export const cycleEntry = () => cyclePeer();

const app = express();
app.use(cors({ origin: "*", credentials: true }));

export function unsafeDecode(payload: string): unknown {
  return serialize.unserialize(payload);
}

export async function loadCustomers(repo: any) {
  return repo.customer.findMany({
    include: {
      orders: { include: { items: true, payments: true } },
      auditHistory: true,
    },
  });
}

export function intersect(left: string[], right: string[]): string[] {
  return left.filter((value) => right.includes(value));
}

export function calculateAndRecordTotal(values: number[]): number {
  const total = values.reduce((sum, value) => sum + value, 0);
  fs.writeFileSync("/tmp/last-total", String(total));
  return total;
}

function expensiveStableLookup(key: string): string {
  for (let index = 0; index < 1_000_000; index += 1) {
    key = `${key}`;
  }
  return key;
}

export function repeatedLookup(keys: string[]): string[] {
  return keys.map((key) => expensiveStableLookup(key));
}

export function charge(kind: string, amount: number): void {
  if (kind === "card") console.log("card", amount);
  if (kind === "bank") console.log("bank", amount);
}

export function refund(kind: string, amount: number): void {
  if (kind === "card") console.log("card refund", amount);
  if (kind === "bank") console.log("bank refund", amount);
}

export class Eligibility {
  public eligible(input: number): boolean {
    return this.score(input) > 500;
  }

  private score(input: number): number {
    const normalized = Math.max(0, Math.min(input, 1000));
    const riskBand = normalized > 800 ? 3 : normalized > 500 ? 2 : 1;
    return normalized - riskBand * 25;
  }
}

export function isEnabled(value: boolean): boolean {
  return !!value === true ? true : false;
}
