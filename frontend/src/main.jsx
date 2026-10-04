import React, { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import {
  Activity,
  Atom,
  ChevronRight,
  CircleDot,
  Cpu,
  FlaskConical,
  Play,
  Sparkles
} from 'lucide-react';

import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from 'recharts';

import './styles.css';


// ======================================================
// BACKEND API
// ======================================================

const API = import.meta.env.VITE_API_URL
  ? import.meta.env.VITE_API_URL
  : '/api';


// ======================================================
// FALLBACK MOLECULE DATA
// ======================================================

const fallback = [
  {
    id: 'H2',
    formula: 'H₂',
    name: 'Hydrogen',
    qubits: 4,
    atoms: [
      { element: 'H', x: -0.37 },
      { element: 'H', x: 0.37 }
    ]
  },
  {
    id: 'LiH',
    formula: 'LiH',
    name: 'Lithium hydride',
    qubits: 6,
    atoms: [
      { element: 'Li', x: -0.78 },
      { element: 'H', x: 0.78 }
    ]
  },
  {
    id: 'BeH2',
    formula: 'BeH₂',
    name: 'Beryllium dihydride',
    qubits: 8,
    atoms: [
      { element: 'H', x: -1.31 },
      { element: 'Be', x: 0 },
      { element: 'H', x: 1.31 }
    ]
  },
  {
    id: 'N2',
    formula: 'N₂',
    name: 'Nitrogen',
    qubits: 10,
    atoms: [
      { element: 'N', x: -0.55 },
      { element: 'N', x: 0.55 }
    ]
  },
  {
    id: 'CO2',
    formula: 'CO₂',
    name: 'Carbon dioxide',
    qubits: 12,
    atoms: [
      { element: 'O', x: -1.16 },
      { element: 'C', x: 0 },
      { element: 'O', x: 1.16 }
    ]
  },
  {
    id: 'H2O',
    formula: 'H₂O',
    name: 'Water',
    qubits: 8,
    atoms: [
      { element: 'H', x: -0.76 },
      { element: 'O', x: 0 },
      { element: 'H', x: 0.76 }
    ]
  },
  { id: 'Benzene', formula: 'C₆H₆', name: 'Benzene', qubits: 12, atoms: [
    { element: 'C', x: -1.45 }, { element: 'C', x: -0.70 }, { element: 'C', x: 0.70 },
    { element: 'C', x: 1.45 }, { element: 'C', x: 0.70 }, { element: 'C', x: -0.70 },
    { element: 'H', x: -2.50 }, { element: 'H', x: -1.30 }, { element: 'H', x: 1.30 },
    { element: 'H', x: 2.50 }, { element: 'H', x: 1.30 }, { element: 'H', x: -1.30 }
  ] },
  { id: 'Aspirin', formula: 'C₉H₈O₄', name: 'Acetylsalicylic acid', qubits: 12, atoms: [
    { element: 'C', x: -2.8 }, { element: 'C', x: -1.4 }, { element: 'C', x: 2.8 }, { element: 'C', x: 1.4 },
    { element: 'O', x: -3.6 }, { element: 'O', x: 1.4 }, { element: 'O', x: 3.6 }, { element: 'O', x: -0.2 },
    { element: 'C', x: -0.2 }, { element: 'C', x: 1.8 }, { element: 'C', x: 0.4 }, { element: 'C', x: -1.6 },
    { element: 'H', x: -3.2 }, { element: 'H', x: 3.2 }, { element: 'H', x: 0.6 }, { element: 'H', x: -2.4 },
    { element: 'H', x: 1.6 }, { element: 'H', x: -1.2 }, { element: 'H', x: 0.2 }
  ] },
  { id: 'Paracetamol', formula: 'C₈H₉NO₂', name: 'Acetaminophen', qubits: 12, atoms: [
    { element: 'C', x: -2.2 }, { element: 'C', x: -1.0 }, { element: 'C', x: 1.0 }, { element: 'C', x: 2.2 },
    { element: 'N', x: 0.0 }, { element: 'O', x: 3.2 }, { element: 'O', x: -3.2 }, { element: 'C', x: 0.0 },
    { element: 'H', x: -1.6 }, { element: 'H', x: 1.6 }, { element: 'H', x: -3.0 }, { element: 'H', x: 3.0 },
    { element: 'H', x: -2.8 }, { element: 'H', x: 0.8 }, { element: 'H', x: -0.8 }, { element: 'C', x: 1.4 },
    { element: 'H', x: 2.0 }
  ] },
  { id: 'Caffeine', formula: 'C₈H₁₀N₄O₂', name: 'Caffeine', qubits: 12, atoms: [
    { element: 'C', x: -2.4 }, { element: 'C', x: -1.0 }, { element: 'C', x: 1.0 }, { element: 'C', x: 2.4 },
    { element: 'N', x: -1.8 }, { element: 'N', x: 0.0 }, { element: 'N', x: 1.8 }, { element: 'N', x: 0.8 },
    { element: 'O', x: -3.6 }, { element: 'O', x: 3.6 }, { element: 'C', x: 0.0 }, { element: 'C', x: 2.0 },
    { element: 'C', x: -0.8 }, { element: 'C', x: 1.2 }, { element: 'H', x: 0.4 }, { element: 'H', x: -2.6 },
    { element: 'H', x: 1.6 }, { element: 'H', x: -1.2 }, { element: 'H', x: 2.8 }, { element: 'H', x: -0.2 },
    { element: 'H', x: 1.8 }, { element: 'H', x: -3.2 }
  ] },
  { id: 'Ibuprofen', formula: 'C₁₃H₁₈O₂', name: 'Ibuprofen', qubits: 12, atoms: [
    { element: 'C', x: -3.0 }, { element: 'C', x: -1.8 }, { element: 'C', x: -0.6 }, { element: 'C', x: 0.6 },
    { element: 'C', x: 1.8 }, { element: 'C', x: 3.0 }, { element: 'C', x: 4.2 }, { element: 'C', x: -2.4 },
    { element: 'C', x: -4.2 }, { element: 'O', x: 3.6 }, { element: 'O', x: 4.8 }, { element: 'C', x: 2.4 },
    { element: 'C', x: 1.2 }, { element: 'H', x: -1.2 }, { element: 'H', x: -3.6 }, { element: 'H', x: -4.8 },
    { element: 'H', x: 2.4 }, { element: 'H', x: 3.4 }, { element: 'H', x: 4.6 }, { element: 'H', x: 5.2 },
    { element: 'H', x: 0.6 }, { element: 'H', x: 2.0 }, { element: 'H', x: 0.2 }, { element: 'H', x: -2.0 },
    { element: 'H', x: -1.4 }, { element: 'H', x: -3.0 }, { element: 'H', x: 1.0 }, { element: 'H', x: 3.0 }
  ] },
  { id: 'Amoxicillin', formula: 'C₁₆H₁₉N₃O₅S', name: 'Amoxicillin', qubits: 12, atoms: [
    { element: 'C', x: -3.4 }, { element: 'C', x: -2.0 }, { element: 'C', x: 2.0 }, { element: 'C', x: 3.4 },
    { element: 'N', x: 0.0 }, { element: 'N', x: 1.0 }, { element: 'N', x: -1.4 }, { element: 'O', x: 3.8 },
    { element: 'O', x: -3.8 }, { element: 'S', x: 2.6 }, { element: 'O', x: 0.4 }, { element: 'O', x: -0.8 },
    { element: 'C', x: 1.8 }, { element: 'C', x: 0.6 }, { element: 'C', x: -1.8 }, { element: 'C', x: -0.4 },
    { element: 'C', x: 2.4 }, { element: 'C', x: 4.0 }, { element: 'H', x: 1.2 }, { element: 'H', x: -2.6 },
    { element: 'H', x: 3.2 }, { element: 'H', x: -1.2 }, { element: 'H', x: 4.6 }, { element: 'H', x: 2.0 },
    { element: 'H', x: 0.0 }, { element: 'H', x: -0.2 }, { element: 'H', x: 1.6 }
  ] },
  { id: 'Metformin', formula: 'C₄H₁₁N₅', name: 'Metformin', qubits: 12, atoms: [
    { element: 'C', x: -2.0 }, { element: 'C', x: 0.0 }, { element: 'C', x: 2.0 }, { element: 'C', x: 1.0 },
    { element: 'N', x: -1.0 }, { element: 'N', x: 0.0 }, { element: 'N', x: 2.0 }, { element: 'N', x: 3.0 },
    { element: 'N', x: -2.4 }, { element: 'H', x: -3.0 }, { element: 'H', x: 1.2 }, { element: 'H', x: 0.4 },
    { element: 'H', x: -1.6 }, { element: 'H', x: 2.4 }, { element: 'H', x: 2.0 }, { element: 'H', x: -0.6 },
    { element: 'H', x: 1.8 }, { element: 'H', x: 3.6 }, { element: 'H', x: -1.0 }
  ] },
  { id: 'VitaminC', formula: 'C₆H₈O₆', name: 'Ascorbic acid', qubits: 12, atoms: [
    { element: 'C', x: -2.6 }, { element: 'C', x: -1.4 }, { element: 'C', x: 1.4 }, { element: 'C', x: 2.6 },
    { element: 'O', x: -3.4 }, { element: 'O', x: 3.4 }, { element: 'O', x: 0.2 }, { element: 'O', x: -0.8 },
    { element: 'O', x: 2.0 }, { element: 'O', x: -2.0 }, { element: 'C', x: 0.2 }, { element: 'C', x: -0.2 },
    { element: 'H', x: -3.0 }, { element: 'H', x: -1.0 }, { element: 'H', x: 1.0 }, { element: 'H', x: 3.0 },
    { element: 'H', x: 2.4 }, { element: 'H', x: -2.4 }, { element: 'H', x: 0.4 }
  ] }
];


// ======================================================
// MOLECULE VISUALIZATION
// ======================================================

function bondOrder(elemA, elemB) {
  const pair = [elemA, elemB].sort().join('');

  // Triple bonds (e.g., N≡N, C≡N, C≡C)
  if (pair === 'NN' || pair === 'CN') return 3;

  // Common double bonds in drug molecules: C=O, C=N, C=S, S=O, N=O
  if (pair === 'CO' || pair === 'CN' || pair === 'CS' || pair === 'OS' || pair === 'SO') return 2;

  return 1;
}

function elementClass(elem) {
  return 'atom ' + elem.toLowerCase();
}

function Molecule({ atoms = [], active = true, zoom = false }) {

  if (!atoms.length) {
    return <div className="molecule" />;
  }

  const min = Math.min(...atoms.map(a => a.x));
  const max = Math.max(...atoms.map(a => a.x));

  const range = max - min || 1;

  return (
    <div className={'molecule' + (zoom ? ' zoom' : '')}>

      {atoms.map((a, i) => (
        <React.Fragment key={i}>

          {i > 0 && (() => {
            const n = bondOrder(atoms[i - 1].element, a.element);
            const left = 16 + ((atoms[i - 1].x - min) / range) * 68;
            const width = ((a.x - atoms[i - 1].x) / range) * 68;
            const gap = n > 1 ? 3.5 : 0;

            return (
              <span
                className={'bondgroup bond' + n + (active ? ' scanning' : '')}
                style={{ left: `${left}%`, width: `${width}%` }}
              >
                {Array.from({ length: n }, (_, k) => (
                  <i
                    key={k}
                    className="bond"
                    style={{
                      top: `${50 + (k - (n - 1) / 2) * gap}px`
                    }}
                  />
                ))}
              </span>
            );
          })()}

          <b
            className={elementClass(a.element) + (active ? ' scanning' : '')}
            style={{
              left: `${16 + ((a.x - min) / range) * 68}%`
            }}
          >
            {a.element}
          </b>

        </React.Fragment>
      ))}

    </div>
  );
}


// ======================================================
// QUANTUM CIRCUIT
// ======================================================

function Circuit({ result }) {

  const q = result?.qubits || 4;
  const gates = result?.circuit || [];

  return (
    <div className="circuit">

      {Array.from({ length: q }, (_, qIndex) => (

        <div className="wire" key={qIndex}>

          <span>
            q{qIndex}
          </span>

          {gates
            .filter(g => g.q === qIndex)
            .map((g, i) => (

              <em
                key={i}
                className={g.gate === 'CX' ? 'cx' : ''}
              >
                {g.gate === 'CX' ? '●' : g.gate}
              </em>

            ))}

        </div>

      ))}

    </div>
  );
}


// ======================================================
// MAIN APP
// ======================================================

function App() {

  const [molecules, setMolecules] = useState(fallback);

  const [selected, setSelected] = useState([
    'H2',
    'LiH',
    'BeH2',
    'N2',
    'CO2',
    'H2O'
  ]);

  const [job, setJob] = useState(null);

  const [focus, setFocus] = useState(null);

  const [loading, setLoading] = useState(false);

  const [error, setError] = useState('');


// ======================================================
// LOAD MOLECULES
// ======================================================

  useEffect(() => {

    fetch(`${API}/molecules`)

      .then(response => {

        if (!response.ok) {
          throw new Error(
            `Backend returned ${response.status}`
          );
        }

        return response.json();
      })

      .then(data => {
        console.log('Molecules loaded:', data);
        setMolecules(data);
        const ids = data.map(item => item.id);
        setSelected(current => {
          const kept = current.filter(id => ids.includes(id));
          return kept.length ? kept : ids;
        });
      })

      .catch(err => {

        console.error(
          'Could not load molecules:',
          err
        );

        setError(
          'Could not connect to the backend. Make sure FastAPI is running on port 8000.'
        );
      });

  }, []);


// ======================================================
// POLL SCREENING JOB
// ======================================================

  useEffect(() => {

    if (!job?.id) {
      return;
    }

    if (
      job.status === 'complete' ||
      job.status === 'failed'
    ) {
      return;
    }

    console.log(
      'Starting screening polling:',
      job.id
    );

    const timer = setInterval(async () => {

      try {

        const response = await fetch(
          `${API}/screenings/${job.id}`
        );

        if (!response.ok) {

          throw new Error(
            `Screening status returned ${response.status}`
          );
        }

        const updatedJob = await response.json();

        console.log(
          'Screening update:',
          updatedJob
        );

        setJob(updatedJob);

        if (
          updatedJob.results &&
          updatedJob.results.length > 0
        ) {

          setFocus(current =>
            current || updatedJob.results[0]
          );
        }

      } catch (err) {

        console.error(
          'Polling error:',
          err
        );

        setError(
          'Could not retrieve screening progress from the backend.'
        );

      }

    }, 600);

    return () => {
      clearInterval(timer);
    };

  }, [job?.id, job?.status]);


// ======================================================
// RUN SCREENING
// ======================================================

  const run = async () => {

    if (!selected.length) {

      setError(
        'Please select at least one molecule.'
      );

      return;
    }

    setLoading(true);

    setError('');

    setFocus(null);

    setJob(null);

    console.log(
      'Starting screening for:',
      selected
    );

    try {

      const response = await fetch(
        `${API}/screenings`,
        {
          method: 'POST',

          headers: {
            'Content-Type': 'application/json'
          },

          body: JSON.stringify({
            molecules: selected,
            max_iterations: 72
          })
        }
      );


      // -----------------------------------------------
      // CHECK HTTP RESPONSE
      // -----------------------------------------------

      if (!response.ok) {

        let message = `Backend returned ${response.status}`;

        try {

          const errorData =
            await response.json();

          if (errorData.detail) {
            message = errorData.detail;
          }

        } catch {
          // Ignore JSON parsing failure
        }

        throw new Error(message);
      }


      // -----------------------------------------------
      // GET JOB
      // -----------------------------------------------

      const newJob = await response.json();

      console.log(
        'Screening job created:',
        newJob
      );


      if (!newJob.id) {

        throw new Error(
          'Backend did not return a screening job ID.'
        );
      }


      setJob(newJob);

    } catch (err) {

      console.error(
        'SCREENING ERROR:',
        err
      );

      setError(
        err.message ||
        'Unable to start screening.'
      );

    } finally {

      setLoading(false);

    }
  };


// ======================================================
// SELECT / DESELECT MOLECULE
// ======================================================

  const toggle = id => {

    setSelected(current => {

      if (current.includes(id)) {

        return current.filter(
          x => x !== id
        );

      }

      return [
        ...current,
        id
      ];

    });

  };


// ======================================================
// CURRENT RESULT
// ======================================================

  const result =
    focus ||
    job?.results?.[0];


// ======================================================
// UI
// ======================================================

  return (

    <main>

      {/* NAVIGATION */}

      <nav>

        <div className="brand">

          <Atom />

          AURORA

          <span>
            QUANTUM
          </span>

        </div>

        <div className="navright">

          <CircleDot size={15} />

          Hardware-ready

          <button className="avatar">
            AR
          </button>

        </div>

      </nav>


      {/* HERO */}

      <section className="hero">

        <div>

          <p className="eyebrow">
            VQE MOLECULAR DISCOVERY PLATFORM
          </p>

          <h1>
            Screen stability
            <br />
            <i>before synthesis.</i>
          </h1>

          <p className="sub">
            Use variational quantum simulation
            to rank candidate molecules by
            ground-state energy.
          </p>

        </div>


        <div className="orbital">

          <div className="orbit o1" />

          <div className="orbit o2" />

          <div className="nucleus">
            ψ
          </div>

        </div>

      </section>


      {/* WORKSPACE */}

      <section className="workspace">


        {/* CANDIDATE LIBRARY */}

        <aside>

          <p className="label">
            CANDIDATE LIBRARY
          </p>

          <p className="demo-note">
            {molecules.length} demo molecules · educational VQE benchmarks
          </p>


          <div className="candidate-grid">

          {molecules.map(m => (

            <button
              className={
                'candidate ' +
                (
                  selected.includes(m.id)
                    ? 'selected'
                    : ''
                )
              }

              onClick={() =>
                toggle(m.id)
              }

              key={m.id}
            >

              <Molecule
                atoms={m.atoms}
                active={
                  job?.active_molecule === m.id
                }
              />

              <span>

                <b>
                  {m.formula}
                </b>

                <small>
                  {m.name} · {m.qubits} qubits
                </small>

              </span>

              <span className="check">

                {
                  selected.includes(m.id)
                    ? '✓'
                    : '+'
                }

              </span>

            </button>

          ))}

          </div>


          {/* RUN BUTTON (LIBRARY) */}

          <button
            disabled={
              !selected.length ||
              loading
            }

            className="run"

            onClick={run}
          >

            <Play
              fill="currentColor"
              size={16}
            />

            {
              loading
                ? 'Starting…'
                : 'Run screening'
            }

          </button>


          <p className="note">
            UCCSD ansatz · SPSA optimizer
          </p>


          {/* ERROR MESSAGE */}

          {error && (

            <div
              style={{
                marginTop: '12px',
                padding: '10px',
                border: '1px solid #6b3434',
                background: '#241416',
                color: '#ff9b9b',
                fontSize: '11px',
                lineHeight: '1.5',
                borderRadius: '4px'
              }}
            >

              <b>
                SCREENING ERROR
              </b>

              <br />

              {error}

            </div>

          )}

        </aside>


        {/* DASHBOARD */}

        <div className="dashboard">


          {/* STATUS */}

          <div className="status">

            <div>

              <p className="label">
                LIVE SCREENING
              </p>

              <b>

                {
                  job?.status === 'complete'
                    ? 'Screening completed'
                    : job?.status === 'failed'
                      ? 'Screening failed'
                      : job?.status === 'queued'
                        ? 'Queued…'
                        : job?.active_stage ||
                          (job ? 'Starting…' : 'Ready to begin')
                }

              </b>

              <span>

                {
                  job?.active_molecule &&
                  `Processing ${job.active_molecule}`
                }

              </span>

            </div>


            <div className="progress">

              <b>
                {job?.progress || 0}%
              </b>

              <div>

                <i
                  style={{
                    width:
                      `${job?.progress || 0}%`
                  }}
                />

              </div>

            </div>

            <button
              disabled={
                !selected.length ||
                loading
              }

              className="run compact"

              onClick={run}
            >

              <Play
                fill="currentColor"
                size={16}
              />

              {
                loading
                  ? 'Starting…'
                  : 'Run screening'
              }

            </button>

          </div>


          {/* RESULTS GRID */}

          <div className="grid">


            {/* ACTIVE MOLECULE */}

            <article className="panel structure">

              <div className="panelhead">

                <span>
                  <Sparkles size={16} />
                  ACTIVE MOLECULE
                </span>

                <b>
                  {result?.formula || '—'}
                </b>

              </div>


              {result ? (

                <>

                  <Molecule
                    atoms={result.atoms}
                  />

                  <div className="facts">

                    <span>
                      QUBITS
                      <b>
                        {result.qubits}
                      </b>
                    </span>

                    <span>
                      ELECTRONS
                      <b>
                        {result.electrons}
                      </b>
                    </span>

                    <span>
                      ANSATZ
                      <b>
                        UCCSD
                      </b>
                    </span>

                  </div>

                </>

              ) : (

                <div className="empty">

                  <FlaskConical />

                  Select candidates,
                  then run a screen.

                </div>

              )}

            </article>


            {/* VQE CHART */}

            <article className="panel chart">

              <div className="panelhead">

                <span>
                  <Activity size={16} />
                  VQE CONVERGENCE
                </span>

                <b>
                  {result ? 'Converged' : ''}
                </b>

              </div>


              {result ? (

                <ResponsiveContainer
                  width="100%"
                  height={210}
                >

                  <AreaChart
                    data={result.convergence}
                  >

                    <defs>

                      <linearGradient
                        id="e"
                        x1="0"
                        x2="0"
                        y1="0"
                        y2="1"
                      >

                        <stop
                          stopColor="#9bffb0"
                          stopOpacity=".45"
                        />

                        <stop
                          offset="1"
                          stopColor="#9bffb0"
                          stopOpacity="0"
                        />

                      </linearGradient>

                    </defs>


                    <CartesianGrid
                      stroke="#24313d"
                      vertical={false}
                    />

                    <XAxis
                      dataKey="iteration"
                      stroke="#738394"
                      fontSize={10}
                    />

                    <YAxis
                      domain={[
                        'auto',
                        'auto'
                      ]}
                      stroke="#738394"
                      fontSize={10}
                    />

                    <Tooltip />

                    <Area
                      dataKey="energy"
                      stroke="#9bffb0"
                      fill="url(#e)"
                      strokeWidth={2}
                    />

                  </AreaChart>

                </ResponsiveContainer>

              ) : (

                <div className="empty">

                  <Activity />

                  Convergence trace
                  will appear here.

                </div>

              )}

            </article>


            {/* QUANTUM CIRCUIT */}

            <article className="panel circuitpanel">

              <div className="panelhead">

                <span>
                  <Cpu size={16} />
                  UCCSD QUANTUM CIRCUIT
                </span>

                <b>
                  Mapped
                </b>

              </div>


              <Circuit
                result={result}
              />

              <small className="circuitnote">

                Jordan–Wigner mapping ·
                {result?.qubits || 4}
                qubit register

              </small>

            </article>

          </div>


          {/* RANKING */}

          <article className="panel rankings">

            <div className="panelhead">

              <span>

                <ChevronRight size={16} />

                STABILITY RANKING

              </span>

              <b>

                {job?.results?.length || 0}
                {' / '}
                {selected.length}
                {' complete'}

              </b>

            </div>


            <div className="table">

              <div className="tr th">

                <span>
                  RANK
                </span>

                <span>
                  MOLECULE
                </span>

                <span>
                  GROUND-STATE ENERGY
                </span>

                <span>
                  BINDING ENERGY
                </span>

                <span>
                  ERROR
                </span>

              </div>


              {job?.results?.map(r => (

                <button

                  className={
                    'tr ' +
                    (
                      focus?.molecule === r.molecule
                        ? 'active'
                        : ''
                    )
                  }

                  onClick={() =>
                    setFocus(r)
                  }

                  key={r.molecule}
                >

                  <span className="rank">
                    0{r.rank}
                  </span>

                  <span>

                    <b>
                      {r.formula}
                    </b>

                    <small>
                      {r.name}
                    </small>

                  </span>

                  <span>
                    {r.total_energy_hartree.toFixed(5)}
                    {' Ha'}
                  </span>

                  <span className="good">
                    {r.binding_energy_hartree.toFixed(4)}
                    {' Ha'}
                  </span>

                  <span>
                    {r.error_millihartree}
                    {' mHa'}
                  </span>

                </button>

              ))}


              {!job?.results?.length && (

                <div className="empty rowempty">

                  Awaiting quantum estimates…

                </div>

              )}

            </div>

          </article>

        </div>

      </section>

    </main>
  );
}


// ======================================================
// START REACT
// ======================================================

createRoot(
  document.getElementById('root')
).render(
  <App />
);