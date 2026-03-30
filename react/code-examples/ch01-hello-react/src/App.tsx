import { useState } from "react";

function Greeting({ name }: { name: string }) {
  return (
    <h2 className="text-2xl font-semibold text-gray-700">
      Hello, {name}! Welcome to React 19
    </h2>
  );
}

function Counter() {
  const [count, setCount] = useState(0);

  return (
    <div className="mt-6 flex items-center gap-4">
      <button
        className="rounded-lg bg-blue-600 px-6 py-2 text-white font-medium
                   hover:bg-blue-700 active:bg-blue-800 transition-colors"
        onClick={() => setCount((c) => c + 1)}
      >
        Count: {count}
      </button>
      <span className="text-gray-500 text-sm">
        Click the button to increment
      </span>
    </div>
  );
}

function FeatureList() {
  const features = [
    "Server Components",
    "Actions & useActionState",
    "use() API",
    "React Compiler",
    "Ref as a Prop",
    "Document Metadata",
    "Improved Error Handling",
  ];

  return (
    <div className="mt-8">
      <h3 className="text-lg font-semibold text-gray-700 mb-3">
        React 19 Key Features
      </h3>
      <ul className="space-y-2">
        {features.map((feature) => (
          <li
            key={feature}
            className="flex items-center gap-2 text-gray-600"
          >
            <span className="h-2 w-2 rounded-full bg-blue-500" />
            {feature}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default function App() {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-8">
      <div className="max-w-xl w-full bg-white rounded-2xl shadow-lg p-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">
          Chapter 1
        </h1>
        <p className="text-gray-400 mb-6">Hello React 19</p>
        <Greeting name="Reader" />
        <Counter />
        <FeatureList />
      </div>
    </div>
  );
}
