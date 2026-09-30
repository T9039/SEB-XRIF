import type { ReactNode } from "react";
import {
  Alert,
  AlertDescription,
  Badge,
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@humanity-erp/ui";

function Section({
  step,
  title,
  lead,
  children,
}: {
  step?: string;
  title: string;
  lead?: string;
  children: ReactNode;
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          {step ? <Badge>{step}</Badge> : null}
          {title}
        </CardTitle>
        {lead ? <CardDescription>{lead}</CardDescription> : null}
      </CardHeader>
      <CardContent className="flex flex-col gap-3 text-sm leading-relaxed">{children}</CardContent>
    </Card>
  );
}

function Point({ term, children }: { term: string; children: ReactNode }) {
  return (
    <div className="flex flex-col gap-0.5">
      <span className="font-medium">{term}</span>
      <span className="text-muted-foreground">{children}</span>
    </div>
  );
}

/** A friendly, plain-language guide to the framework for non-specialists. */
export function GuidePanel() {
  return (
    <div className="flex max-w-3xl flex-col gap-4">
      <Card>
        <CardHeader>
          <CardTitle>What is this?</CardTitle>
          <CardDescription>A plain-language guide for first-time users</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col gap-3 text-sm leading-relaxed">
          <p>
            This dashboard is the working part of a research project about teaching with virtual and
            augmented reality. Its purpose is to help a school or university answer one question
            honestly:{" "}
            <strong>
              is this kind of teaching actually helping students learn, and does the learning last?
            </strong>
          </p>
          <p>
            It does this in three broad steps. It collects what students do while they learn, it
            builds a simple model that can flag students who may need support early, and it compares
            results before, right after, and months after the teaching, using the same measures
            everywhere so different institutions can be compared fairly.
          </p>
          <p className="text-muted-foreground">
            Importantly, this is a reusable recipe, not a single finished product. The project
            includes some example data to show how it works, but the real proof will come from a
            future pilot with real students.
          </p>
        </CardContent>
      </Card>

      <Section
        title="The tabs, and what each one is for"
        lead="You move between these using the menu on the left. The buttons in the top bar apply to everything."
      >
        <Point term="Overview">
          A summary at a glance: how well the model is doing, how the predicted support groups are
          split, and the before/after learning results (empty until real pilot data is added).
        </Point>
        <Point term="Predict">
          Fill in what you know about a learner, and the system suggests a{" "}
          <strong>support band</strong> — a gentle nudge about who might need attention, never a
          label or a decision about a person.
        </Point>
        <Point term="Data">
          The raw list of learners and their details, in a sortable and searchable table.
        </Point>
        <Point term="Diagnostics">
          How much you can trust the model: how accurate it is, where it gets things wrong, and how
          confident its answers really are. This is the “show your workings” tab.
        </Point>
        <Point term="Explore">
          The XR (virtual-reality) side: how engagement changes over time, which learners are at
          risk of dropping off, and how ordinary classroom measures line up with virtual-reality
          ones.
        </Point>
        <Point term="Studio">
          Make your own charts and keep them, so you can explore the numbers yourself.
        </Point>
        <Point term="Datasets">
          Add your own data. You can check a file, tidy up a spreadsheet, download a simplified
          version of a complicated file, and then train a model on it.
        </Point>
      </Section>

      <Section title="The buttons in the top bar" lead="These control the whole page.">
        <Point term="Data source">
          Chooses <em>which</em> body of data you are looking at — the built-in classroom example,
          or one of the virtual-reality pilots. Every tab updates to match.
        </Point>
        <Point term="Light / dark">Switches the screen between a bright and a dim look.</Point>
      </Section>

      <Section
        title="What kind of data does it accept?"
        lead="Three ways in, from easiest to most technical."
      >
        <Point term="1. Activity records in the standard format">
          The system expects a standard record of learning activity — the “who did what, and when”
          of a lesson. If your software already exports that standard format, you can add it as-is
          and train straight away.
        </Point>
        <Point term="2. A simple spreadsheet">
          An ordinary CSV spreadsheet works too. You point out which column is the outcome you want
          predicted and which columns are the clues, and the system does the rest. It will never
          make up data: if the outcome column is missing, it declines rather than guess.
        </Point>
        <Point term="3. A complicated activity file, tidied first">
          If you have activity records in a different shape, you can flatten them into a simple
          table in one click, then treat it like a spreadsheet.
        </Point>
        <p className="text-muted-foreground">
          Whatever the source, the outcome you want predicted must be defined by a person. The
          system will not invent a target.
        </p>
      </Section>

      <Section
        title="The measures it insists on"
        lead="Every user reports the same things, so results can be compared fairly."
      >
        <Point term="How accurate the model is">
          Measured with standard accuracy and F1 scores, tested on data the model has not seen, with
          a range of likely values so a lucky result is not mistaken for a good one.
        </Point>
        <Point term="How honest its confidence is">
          When the model says it is 80% sure, it should be right about 80% of the time. This is
          checked.
        </Point>
        <Point term="How usable people find it">
          A standard questionnaire (the System Usability Scale) scored out of 100, compared against
          a benchmark of 76.6.
        </Point>
        <Point term="How much learning happened, and whether it lasted">
          A standard effect size (Cohen's d) measured three times: before the teaching, right after,
          and one term later. The delayed measurement is what shows whether learning stuck.
        </Point>
      </Section>

      <Section title="Step by step">
        <ol className="flex list-decimal flex-col gap-2 pl-5">
          <li>
            Open the dashboard and look around the <strong>Overview</strong>, <strong>Data</strong>{" "}
            and <strong>Diagnostics</strong> tabs to see the built-in example.
          </li>
          <li>
            In <strong>Explore</strong>, switch the <em>Data source</em> to a virtual-reality pilot
            to see engagement and drop-off.
          </li>
          <li>
            In <strong>Datasets</strong>, add your own data: check the file, tidy it if needed, then
            train.
          </li>
          <li>
            Switch the <em>Data source</em> to your data and use <strong>Predict</strong> and{" "}
            <strong>Diagnostics</strong>.
          </li>
          <li>
            Run the before/after/one-term-later questionnaires with your students and record the
            results.
          </li>
          <li>
            Read the learning results in <strong>Overview</strong> and report them using the fixed
            measures above.
          </li>
        </ol>
      </Section>

      <Section title="Honest limits — please read these">
        <ul className="flex list-disc flex-col gap-2 pl-5">
          <li>
            The built-in example is ordinary school data, <strong>not</strong> virtual reality. It
            demonstrates the method; it does not prove anything about XR learning.
          </li>
          <li>
            A person must decide what outcome to predict. If your data has no outcome, the system
            refuses rather than making one up.
          </li>
          <li>
            The virtual-reality “risk” band is about engagement and dropping off — it is not a grade
            and not a judgement of a student.
          </li>
          <li>
            Small groups give uncertain answers. The system reports that uncertainty instead of
            hiding it.
          </li>
          <li>This is a prototype being tested. It is expected to change.</li>
        </ul>
      </Section>

      <Alert>
        <AlertDescription>
          Found something confusing or broken? Please note what you did, what you expected, and what
          happened — with a screenshot if you can. Blunt feedback is genuinely useful here.
        </AlertDescription>
      </Alert>
    </div>
  );
}
