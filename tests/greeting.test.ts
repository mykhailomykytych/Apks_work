import { describe, expect, it } from "vitest";
import { greeting } from "../src/greeting";

describe("greeting", () => {
  it("DefaultGreeting", () => {
    expect(greeting()).toBe("Hello, World!");
  });

  it("NamedGreeting", () => {
    expect(greeting("KI-407")).toBe("Hello, KI-407!");
  });
});
