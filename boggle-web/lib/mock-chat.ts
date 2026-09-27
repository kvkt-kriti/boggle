export const CHAT_SUGGESTIONS = [
  "Which exams give me the most credit?",
  "I can only fit 4 APs — which 4?",
  "What's the difference between the top two?",
  "Which of these are optional?",
] as const;

type PlanContext = {
  majorName: string;
  schoolName: string;
  recommendations: {
    ap_exam: string;
    best_credits: number | null;
    fit: string;
  }[];
  totalCredits: number;
};

function topByCredits(ctx: PlanContext, n: number) {
  return [...ctx.recommendations]
    .sort((a, b) => (b.best_credits ?? 0) - (a.best_credits ?? 0))
    .slice(0, n);
}

export function mockChatReply(question: string, ctx: PlanContext): string {
  const q = question.toLowerCase();
  const top = topByCredits(ctx, 4);
  const school = ctx.schoolName;
  const major = ctx.majorName;

  if (q.includes("most credit") || q.includes("biggest")) {
    const lines = top.map(
      (r, i) =>
        `${i + 1}. AP ${r.ap_exam} — ${r.best_credits ?? 0} credit hours`,
    );
    return [
      `Looking only at ${school}'s published chart for your ${major} plan, the biggest credit wins are:`,
      "",
      ...lines,
      "",
      "Always confirm the exact number on the official chart before you register.",
    ].join("\n");
  }

  if (q.includes("only fit") || q.includes("which 4") || q.includes("4 ap")) {
    const lines = top.map((r) => `• AP ${r.ap_exam} (${r.best_credits ?? 0} cr)`);
    return [
      `If you can only take four, prioritize the highest-credit exams on ${school}'s chart:`,
      "",
      ...lines,
      "",
      "Core-for-major badges help you stay aligned with your path — but credit totals come straight from the published chart.",
    ].join("\n");
  }

  if (q.includes("difference") || q.includes("top two")) {
    const [a, b] = topByCredits(ctx, 2);
    if (!a || !b) {
      return `Your ${school} plan doesn't have two ranked exams to compare yet.`;
    }
    return [
      `On the published ${school} chart:`,
      "",
      `• AP ${a.ap_exam} awards about ${a.best_credits ?? 0} credits (${a.fit.toLowerCase()}).`,
      `• AP ${b.ap_exam} awards about ${b.best_credits ?? 0} credits (${b.fit.toLowerCase()}).`,
      "",
      "Pick the higher-credit exam if hours matter most; lean on CORE badges when you're optimizing for your major.",
    ].join("\n");
  }

  if (q.includes("optional") || q.includes("nice")) {
    const nice = ctx.recommendations.filter((r) => r.fit === "NICE-TO-HAVE");
    if (!nice.length) {
      return `On this plan, nothing is tagged nice-to-have yet — most exams look like strong or core matches for ${major}.`;
    }
    const lines = nice.slice(0, 5).map((r) => `• AP ${r.ap_exam}`);
    return [
      `These are tagged nice-to-have for ${major} — useful credit, less central to the major:`,
      "",
      ...lines,
      "",
      "They're still real awards from the official chart; skip them first if your schedule is tight.",
    ].join("\n");
  }

  return [
    `I can help you read your ranked ${major} plan for ${school} (about ${ctx.totalCredits} credit hours across ${ctx.recommendations.length} exams).`,
    "",
    "Try a suggestion chip, or ask which exams give the most credit. I only use mock replies grounded in your current plan — not a live AI model.",
  ].join("\n");
}
