import React, { useEffect, useState } from "react";

import {
  NavLink,
  Route,
  Routes,
  useLocation,
  useNavigate,
} from "react-router-dom";

import {
  ArrowRight,
  Bell,
  Boxes,
  Building2,
  ChevronRight,
  CircleDollarSign,
  Factory,
  Gauge,
  Leaf,
  LayoutDashboard,
  Menu,
  PackagePlus,
  Radar as RadarIcon,
  Search,
  Send,
  Settings,
  Sparkles,
  Target,
  TrendingUp,
  Users,
  X,
  Zap,
} from "lucide-react";

import {
  createListing,
  getDashboard,
  getMatches,
  getRequests,
  getListings,
  createRequest,
  acceptRequest,
  seedDemo,
} from "./services/api";


// ============================================================
// NAVIGATION
// ============================================================

const navItems = [
  {
    to: "/",
    label: "Overview",
    icon: LayoutDashboard,
  },
  {
    to: "/listings/new",
    label: "List material",
    icon: PackagePlus,
  },
  {
    to: "/radar",
    label: "Opportunity Radar",
    icon: RadarIcon,
  },
  {
    to: "/requests",
    label: "Exchange requests",
    icon: Send,
  },
  {
    to: "/impact",
    label: "Impact",
    icon: Leaf,
  },
];


// ============================================================
// SHELL
// ============================================================

function Shell({ children }) {
  const [open, setOpen] = useState(false);
  const location = useLocation();

  useEffect(() => {
    setOpen(false);
  }, [location.pathname]);

  return (
    <div className="app-shell">
      <aside
        className={`sidebar ${
          open ? "sidebar-open" : ""
        }`}
      >
        <div className="brand">
          <div className="brand-mark">
            <Zap size={19} fill="currentColor" />
          </div>

          <div>
            <strong>
              Scrap<span>Sync</span>
            </strong>

            <small>Resource intelligence</small>
          </div>
        </div>

        <div className="workspace">
          <div className="workspace-avatar">E</div>

          <div>
            <b>EcoWorks Demo</b>
            <small>Supplier workspace</small>
          </div>

          <ChevronRight size={15} />
        </div>

        <nav>
          <div className="nav-label">WORKSPACE</div>

          {navItems.map(
            ({ to, label, icon: Icon }) => (
              <NavLink
                key={to}
                to={to}
                end={to === "/"}
                className={({ isActive }) =>
                  isActive
                    ? "nav-link active"
                    : "nav-link"
                }
              >
                <Icon size={18} />
                <span>{label}</span>
              </NavLink>
            )
          )}
        </nav>

        <div className="sidebar-bottom">
          <div className="nav-label">SYSTEM</div>

          <a className="nav-link">
            <Settings size={18} />
            <span>Settings</span>
          </a>

          <div className="sidebar-tip">
            <Sparkles size={18} />

            <b>Smart matching</b>

            <p>
              Turn unused material into your next
              business opportunity.
            </p>
          </div>
        </div>
      </aside>

      <main className="main">
        <header className="topbar">
          <button
            className="mobile-menu"
            onClick={() => setOpen(!open)}
          >
            {open ? <X /> : <Menu />}
          </button>

          <div className="crumb">
            <span>Workspace</span>

            <ChevronRight size={14} />

            <b>
              {pageTitle(location.pathname)}
            </b>
          </div>

          <div className="top-actions">
            <button className="icon-btn">
              <Bell size={18} />
              <i />
            </button>

            <div className="user-avatar">EW</div>
          </div>
        </header>

        <div className="page">{children}</div>
      </main>
    </div>
  );
}


// ============================================================
// PAGE TITLE
// ============================================================

function pageTitle(path) {
  if (path === "/") return "Overview";

  if (path.includes("new")) {
    return "List material";
  }

  if (path.includes("radar")) {
    return "Opportunity Radar";
  }

  if (path.includes("requests")) {
    return "Exchange requests";
  }

  if (path.includes("impact")) {
    return "Impact";
  }

  return "ScrapSync";
}


// ============================================================
// STAT CARD
// ============================================================

function StatCard({
  icon: Icon,
  label,
  value,
  note,
  trend,
}) {
  return (
    <div className="stat-card reveal">
      <div className="stat-icon">
        <Icon size={19} />
      </div>

      <div className="stat-label">
        {label}
      </div>

      <div className="stat-value">
        {value}
      </div>

      <div className="stat-note">
        {trend && (
          <span className="positive">
            ↗ {trend}
          </span>
        )}{" "}
        {note}
      </div>
    </div>
  );
}


// ============================================================
// OVERVIEW
// ============================================================

function Overview() {
  const [data, setData] = useState(null);
  const [busy, setBusy] = useState(false);

  const navigate = useNavigate();

  const loadData = async () => {
    try {
      const result = await getDashboard();
      setData(result);
    } catch (error) {
      console.error(
        "Failed to load dashboard:",
        error
      );
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const loadDemo = async () => {
    setBusy(true);

    try {
      await seedDemo();

      const result = await getDashboard();

      setData(result);
    } catch (error) {
      alert(error.message);
    } finally {
      setBusy(false);
    }
  };

  if (!data) {
    return (
      <div className="loading">
        <div className="spinner" />
        Loading workspace…
      </div>
    );
  }

  return (
    <Shell>
      <section className="hero reveal">
        <div>
          <div className="eyebrow">
            <span className="pulse-dot" />
            RESOURCE INTELLIGENCE
          </div>

          <h1>
            Turn surplus into{" "}
            <em>opportunity.</em>
          </h1>

          <p>
            ScrapSync discovers businesses that can
            use the materials your business no
            longer needs.
          </p>

          <div className="hero-actions">
            <button
              className="btn primary"
              onClick={() =>
                navigate("/listings/new")
              }
            >
              List material
              <ArrowRight size={16} />
            </button>

            <button
              className="btn ghost"
              onClick={() =>
                navigate("/radar")
              }
            >
              <RadarIcon size={16} />
              Explore Radar
            </button>
          </div>
        </div>

        <div className="hero-orbit">
          <div className="orbit orbit-1" />
          <div className="orbit orbit-2" />

          <div className="orbit-core">
            <Zap size={28} />
          </div>

          <div className="float-tag tag-a">
            <Leaf size={14} />
            42 kg diverted
          </div>

          <div className="float-tag tag-b">
            <Target size={14} />
            94% match
          </div>
        </div>
      </section>

      <div className="section-head">
        <div>
          <h2>Business snapshot</h2>
          <p>Live from your resource network</p>
        </div>

        <button
          className="text-btn"
          onClick={loadData}
        >
          Refresh data
          <ArrowRight size={15} />
        </button>
      </div>

      <div className="stats-grid">
        <StatCard
          icon={Boxes}
          label="Material listed"
          value={`${Number(
            data.total_material_kg || 0
          ).toLocaleString("en-IN")} kg`}
          note="across active listings"
          trend="+18%"
        />

        <StatCard
          icon={Target}
          label="Opportunities"
          value={data.opportunities || 0}
          note="high-fit matches"
          trend="+6"
        />

        <StatCard
          icon={CircleDollarSign}
          label="Potential value"
          value={`₹${Number(
            data.potential_value || 0
          ).toLocaleString("en-IN")}`}
          note="estimated recoverable value"
          trend="+12%"
        />

        <StatCard
          icon={Leaf}
          label="Potentially diverted"
          value={`${Number(
            data.diverted_kg || 0
          ).toLocaleString("en-IN")} kg`}
          note="from accepted exchanges"
          trend="+24%"
        />
      </div>

      <div className="two-col">
        <div className="panel reveal">
          <div className="panel-head">
            <div>
              <h3>Recent opportunities</h3>
              <p>
                Best matches found by the engine
              </p>
            </div>

            <button
              className="icon-link"
              onClick={() =>
                navigate("/radar")
              }
            >
              <ArrowRight size={17} />
            </button>
          </div>

          {data.top_matches?.length ? (
            data.top_matches.map((match, index) => (
              <OpportunityRow
                key={index}
                match={match}
                onClick={() =>
                  navigate(
                    `/radar?listing=${match.listing_id}`
                  )
                }
              />
            ))
          ) : (
            <Empty
              text="No opportunities yet. Load demo data or list material."
            />
          )}
        </div>

        <div className="panel reveal">
          <div className="panel-head">
            <div>
              <h3>Material mix</h3>
              <p>What your network is moving</p>
            </div>
          </div>

          <div className="bars">
            {(data.material_mix || []).map(
              (item, index) => (
                <div
                  className="bar-row"
                  key={index}
                >
                  <div className="bar-label">
                    <span>{item.name}</span>
                    <b>{item.kg} kg</b>
                  </div>

                  <div className="bar-track">
                    <div
                      style={{
                        width: `${item.percent}%`,
                      }}
                      className="bar-fill"
                    />
                  </div>
                </div>
              )
            )}
          </div>

          <div className="mini-impact">
            <div>
              <Leaf size={17} />

              <span>
                Every accepted exchange contributes
                to a more circular supply chain.
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="demo-banner reveal">
        <div className="demo-icon">
          <Sparkles size={20} />
        </div>

        <div>
          <b>Hackathon demo mode</b>

          <p>
            Use seeded Bengaluru businesses to
            demonstrate the full matching workflow.
          </p>
        </div>

        <button
          className="btn dark"
          onClick={loadDemo}
          disabled={busy}
        >
          {busy
            ? "Loading…"
            : "Load demo network"}
        </button>
      </div>
    </Shell>
  );
}


// ============================================================
// OPPORTUNITY ROW
// ============================================================

function OpportunityRow({
  match,
  onClick,
}) {
  return (
    <button
      className="op-row"
      onClick={onClick}
    >
      <div className="material-mini">
        {match.material_type === "Textile"
          ? "T"
          : match.material_type ===
            "Cardboard"
          ? "C"
          : match.material_type?.[0] || "M"}
      </div>

      <div className="op-main">
        <b>{match.business_name}</b>

        <span>
          {match.material_type} ·{" "}
          {match.quantity} kg
        </span>
      </div>

      <div className="score">
        <strong>{match.score}%</strong>
        <small>match</small>
      </div>

      <ChevronRight
        size={17}
        className="muted"
      />
    </button>
  );
}


// ============================================================
// EMPTY
// ============================================================

function Empty({ text }) {
  return (
    <div className="empty">
      <Search size={22} />
      <span>{text}</span>
    </div>
  );
}


// ============================================================
// CREATE LISTING
// ============================================================

function CreateListing() {
  const navigate = useNavigate();

  const [loading, setLoading] =
    useState(false);

  const [done, setDone] =
    useState(null);

  const [form, setForm] = useState({
    business_id: 1,
    material_type: "Textile",
    material_name: "Cotton fabric scraps",
    quantity: 42,
    unit: "kg",
    quality: "Grade B",
    price_per_unit: 18,
    location: "Bengaluru",
  });

  const update = (key, value) => {
    setForm((current) => ({
      ...current,
      [key]: value,
    }));
  };

  const submit = async (event) => {
    event.preventDefault();

    setLoading(true);

    try {
      const result = await createListing({
        ...form,
        quantity: Number(form.quantity),
        price_per_unit: Number(
          form.price_per_unit
        ),
      });

      setDone(result);

      setTimeout(() => {
        navigate(
          `/radar?listing=${result.id}`
        );
      }, 700);
    } catch (error) {
      alert(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Shell>
      <div className="page-head reveal">
        <div>
          <div className="eyebrow">
            MATERIAL PASSPORT
          </div>

          <h1>List a material</h1>

          <p>
            Give your surplus a structured identity
            so the network can discover its value.
          </p>
        </div>
      </div>

      <div className="form-layout">
        <form
          className="panel form-panel reveal"
          onSubmit={submit}
        >
          <div className="form-section">
            <h3>Material details</h3>

            <p>
              What resource are you making available?
            </p>
          </div>

          <div className="field-grid">
            <Field label="Material name">
              <input
                value={form.material_name}
                onChange={(event) =>
                  update(
                    "material_name",
                    event.target.value
                  )
                }
                required
              />
            </Field>

            <Field label="Category">
              <select
                value={form.material_type}
                onChange={(event) =>
                  update(
                    "material_type",
                    event.target.value
                  )
                }
              >
                <option>Textile</option>
                <option>Cardboard</option>
                <option>Wood</option>
                <option>Paper</option>
              </select>
            </Field>

            <Field label="Quantity">
              <div className="input-suffix">
                <input
                  type="number"
                  min="1"
                  value={form.quantity}
                  onChange={(event) =>
                    update(
                      "quantity",
                      event.target.value
                    )
                  }
                  required
                />

                <span>kg</span>
              </div>
            </Field>

            <Field label="Quality">
              <select
                value={form.quality}
                onChange={(event) =>
                  update(
                    "quality",
                    event.target.value
                  )
                }
              >
                <option>Grade A</option>
                <option>Grade B</option>
                <option>Grade C</option>
              </select>
            </Field>

            <Field label="Asking price">
              <div className="input-prefix">
                <span>₹</span>

                <input
                  type="number"
                  min="0"
                  value={form.price_per_unit}
                  onChange={(event) =>
                    update(
                      "price_per_unit",
                      event.target.value
                    )
                  }
                  required
                />

                <small>/ kg</small>
              </div>
            </Field>

            <Field label="Location">
              <input
                value={form.location}
                onChange={(event) =>
                  update(
                    "location",
                    event.target.value
                  )
                }
                required
              />
            </Field>
          </div>

          <div className="form-section split">
            <div>
              <h3>Material passport</h3>

              <p>
                These attributes power compatibility
                matching.
              </p>
            </div>

            <div className="passport-preview">
              <div className="passport-top">
                <span>LIVE PREVIEW</span>
                <Leaf size={15} />
              </div>

              <b>
                {form.material_name ||
                  "Your material"}
              </b>

              <span>
                {form.material_type} ·{" "}
                {form.quantity} kg ·{" "}
                {form.quality}
              </span>

              <div className="passport-line">
                <span>
                  Potential network value
                </span>

                <strong>
                  ₹
                  {(
                    Number(form.quantity || 0) *
                    Number(
                      form.price_per_unit || 0
                    )
                  ).toLocaleString("en-IN")}
                </strong>
              </div>
            </div>
          </div>

          <div className="form-actions">
            <button
              type="button"
              className="btn ghost"
              onClick={() => navigate("/")}
            >
              Cancel
            </button>

            <button
              className="btn primary"
              disabled={loading}
            >
              {loading
                ? "Publishing…"
                : "Publish & find opportunities"}

              <ArrowRight size={16} />
            </button>
          </div>

          {done && (
            <div className="success-toast">
              <Sparkles size={17} />

              Published successfully — opening
              Opportunity Radar…
            </div>
          )}
        </form>
      </div>
    </Shell>
  );
}


// ============================================================
// FIELD
// ============================================================

function Field({
  label,
  children,
}) {
  return (
    <label className="field">
      <span>{label}</span>
      {children}
    </label>
  );
}


// ============================================================
// OPPORTUNITY RADAR
// ============================================================

function Radar() {
  const [matches, setMatches] =
    useState([]);

  const [listings, setListings] =
    useState([]);

  const [selected, setSelected] =
    useState(null);

  const [loading, setLoading] =
    useState(true);

  const params =
    new URLSearchParams(
      window.location.search
    );

  const listingId =
    params.get("listing");

  useEffect(() => {
    const loadRadar = async () => {
      try {
        const [
          listingData,
          matchData,
        ] = await Promise.all([
          getListings(),
          getMatches(
            listingId || undefined
          ),
        ]);

        setListings(listingData);
        setMatches(matchData);

        if (
          listingData.find(
            (item) =>
              String(item.id) ===
              listingId
          )
        ) {
          setSelected(
            Number(listingId)
          );
        }
      } catch (error) {
        console.error(
          "Failed to load Radar:",
          error
        );
      } finally {
        setLoading(false);
      }
    };

    loadRadar();
  }, [listingId]);

  const run = async (id) => {
    setSelected(id);
    setLoading(true);

    try {
      const result =
        await getMatches(id);

      setMatches(result);
    } catch (error) {
      alert(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Shell>
      <div className="page-head reveal">
        <div>
          <div className="eyebrow">
            <span className="pulse-dot" />
            LIVE MATCHING ENGINE
          </div>

          <h1>Opportunity Radar</h1>

          <p>
            We find businesses that could use
            what you already have.
          </p>
        </div>

        <div className="radar-status">
          <span className="pulse-dot" />
          Engine online
        </div>
      </div>

      <div className="radar-layout">
        <aside className="panel listing-picker reveal">
          <div className="panel-head">
            <div>
              <h3>Your materials</h3>
              <p>Select a resource</p>
            </div>
          </div>

          {listings.map((listing) => (
            <button
              className={`listing-pick ${
                selected === listing.id
                  ? "selected"
                  : ""
              }`}
              key={listing.id}
              onClick={() =>
                run(listing.id)
              }
            >
              <div className="material-mini">
                {listing.material_type?.[0] ||
                  "M"}
              </div>

              <div>
                <b>{listing.material_name}</b>

                <span>
                  {listing.quantity} kg · ₹
                  {listing.price_per_unit}/kg
                </span>
              </div>

              <ChevronRight size={15} />
            </button>
          ))}

          {!listings.length && (
            <Empty text="No listings yet." />
          )}
        </aside>

        <section className="radar-results">
          <div className="radar-title">
            <div>
              <span>
                DISCOVERY RESULTS
              </span>

              <h2>
                {selected
                  ? "Potential business opportunities"
                  : "Select a material"}
              </h2>
            </div>

            <div className="result-count">
              {matches.length} found
            </div>
          </div>

          {loading ? (
            <div className="loading compact">
              <div className="spinner" />
              Running compatibility checks…
            </div>
          ) : (
            matches.map((match, index) => (
              <MatchCard
                key={index}
                match={match}
              />
            ))
          )}

          {!loading &&
            !matches.length && (
              <div className="empty big">
                <RadarIcon size={32} />

                <b>
                  No compatible opportunities
                  found
                </b>

                <span>
                  Try a different material, price
                  or quantity.
                </span>
              </div>
            )}
        </section>
      </div>
    </Shell>
  );
}


// ============================================================
// MATCH CARD
// ============================================================

function MatchCard({ match }) {
  const [open, setOpen] =
    useState(false);

  const [sent, setSent] =
    useState(false);

  const [sending, setSending] =
    useState(false);

  const send = async () => {
    if (sending || sent) return;

    try {
      setSending(true);

      await createRequest({
        listing_id: match.listing_id,
        buyer_id: match.business_id,
        quantity: Math.min(
          match.quantity,
          match.max_quantity
        ),
      });

      setSent(true);
    } catch (error) {
      alert(error.message);
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="match-card reveal">
      <div className="match-top">
        <div className="company-icon">
          <Factory size={19} />
        </div>

        <div className="company">
          <b>{match.business_name}</b>

          <span>
            {match.industry} ·{" "}
            {match.location}
          </span>
        </div>

        <div className="score-big">
          <strong>
            {match.score}%
          </strong>

          <span>compatibility</span>
        </div>
      </div>

      <div className="match-body">
        <div className="match-meta">
          <span>
            <Boxes size={15} />
            Wants {match.material_type}
          </span>

          <span>
            <Gauge size={15} />
            {match.min_quantity ??
              match.quantity}
            -
            {match.max_quantity} kg
          </span>

          <span>
            <CircleDollarSign size={15} />
            Up to ₹
            {match.max_price}/kg
          </span>
        </div>

        <div className="why">
          <div className="why-head">
            <Sparkles size={15} />

            <b>
              Why this is a strong match
            </b>

            <button
              type="button"
              onClick={() =>
                setOpen(!open)
              }
            >
              {open
                ? "Hide"
                : "View reasoning"}
            </button>
          </div>

          {open && (
            <div className="reasons">
              {(match.reasons || []).map(
                (reason, index) => (
                  <div key={index}>
                    <span>✓</span>
                    {reason}
                  </div>
                )
              )}
            </div>
          )}
        </div>
      </div>

      <div className="match-foot">
        <div>
          <small>
            Potential exchange value
          </small>

          <b>
            ₹
            {Number(
              match.potential_value || 0
            ).toLocaleString("en-IN")}
          </b>
        </div>

        <button
          className={`btn ${
            sent ? "success" : "primary"
          }`}
          onClick={send}
          disabled={sent || sending}
        >
          {sending
            ? "Sending…"
            : sent
            ? "Request sent ✓"
            : "Send exchange request"}

          {!sent && !sending && (
            <ArrowRight size={15} />
          )}
        </button>
      </div>
    </div>
  );
}


// ============================================================
// REQUESTS
// ============================================================

function Requests() {
  const [requests, setRequests] =
    useState([]);

  const [loading, setLoading] =
    useState(true);

  const [accepting, setAccepting] =
    useState(null);

  const loadRequests = async () => {
    try {
      setLoading(true);

      const data =
        await getRequests();

      setRequests(data);
    } catch (error) {
      alert(error.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadRequests();
  }, []);

  const handleAccept = async (
    requestId
  ) => {
    try {
      setAccepting(requestId);

      await acceptRequest(requestId);

      await loadRequests();
    } catch (error) {
      alert(error.message);
    } finally {
      setAccepting(null);
    }
  };

  return (
    <Shell>
      <div className="page-head reveal">
        <div>
          <div className="eyebrow">
            NETWORK ACTIVITY
          </div>

          <h1>Exchange requests</h1>

          <p>
            Track interest in your materials and
            close the loop.
          </p>
        </div>
      </div>

      <div className="panel table-panel reveal">
        <div className="panel-head">
          <div>
            <h3>Requests</h3>

            <p>
              Latest activity from the resource
              network
            </p>
          </div>
        </div>

        {loading ? (
          <div className="loading compact">
            <div className="spinner" />
            Loading requests…
          </div>
        ) : requests.length ? (
          <div className="request-list">
            {requests.map((request) => (
              <div
                className="request-row"
                key={request.id}
              >
                <div className="company-icon small">
                  <Building2 size={16} />
                </div>

                <div className="request-main">
                  <b>
                    {request.buyer_name}
                  </b>

                  <span>
                    {request.material_name} ·{" "}
                    {request.quantity} kg
                  </span>
                </div>

                <span
                  className={`status ${request.status}`}
                >
                  {request.status}
                </span>

                <div className="request-value">
                  ₹
                  {Number(
                    request.value || 0
                  ).toLocaleString("en-IN")}
                </div>

                {request.status ===
                  "pending" && (
                  <button
                    className="btn primary"
                    onClick={() =>
                      handleAccept(
                        request.id
                      )
                    }
                    disabled={
                      accepting ===
                      request.id
                    }
                  >
                    {accepting ===
                    request.id
                      ? "Accepting…"
                      : "Accept exchange"}
                  </button>
                )}

                {request.status ===
                  "accepted" && (
                  <span className="request-accepted">
                    ✓ Accepted
                  </span>
                )}
              </div>
            ))}
          </div>
        ) : (
          <Empty
            text="No exchange requests yet. Send one from Opportunity Radar."
          />
        )}
      </div>
    </Shell>
  );
}


// ============================================================
// IMPACT
// ============================================================

function Impact() {
  const [data, setData] =
    useState(null);

  const [error, setError] =
    useState(null);

  const loadImpact = async () => {
    try {
      setError(null);

      const result =
        await getDashboard();

      setData(result);
    } catch (err) {
      console.error(
        "Failed to load impact dashboard:",
        err
      );

      setError(
        err.message ||
          "Failed to load impact dashboard"
      );
    }
  };

  useEffect(() => {
    loadImpact();
  }, []);

  if (error) {
    return (
      <Shell>
        <div className="empty big">
          <Search size={32} />

          <b>
            Unable to load impact data
          </b>

          <span>{error}</span>

          <button
            className="btn primary"
            onClick={loadImpact}
          >
            Try again
          </button>
        </div>
      </Shell>
    );
  }

  if (!data) {
    return (
      <Shell>
        <div className="loading">
          <div className="spinner" />
          Loading impact dashboard…
        </div>
      </Shell>
    );
  }

  const divertedKg = Number(
    data.diverted_kg || 0
  );

  const potentialValue = Number(
    data.potential_value || 0
  );

  const businesses = Number(
    data.businesses || 0
  );

  const acceptedRequests = Number(
    data.accepted_requests || 0
  );

  return (
    <Shell>
      <div className="page-head reveal">
        <div>
          <div className="eyebrow">
            CIRCULARITY INDEX
          </div>

          <h1>Impact dashboard</h1>

          <p>
            Make the value of resource exchange
            visible.
          </p>
        </div>
      </div>

      <div className="impact-hero reveal">
        <div className="impact-leaf">
          <Leaf size={35} />
        </div>

        <div>
          <span>
            POTENTIALLY DIVERTED
          </span>

          <strong>
            {divertedKg.toLocaleString(
              "en-IN"
            )}{" "}
            kg
          </strong>

          <p>
            Material committed through accepted
            exchanges
          </p>
        </div>

        <div className="impact-side">
          <b>
            ₹
            {potentialValue.toLocaleString(
              "en-IN"
            )}
          </b>

          <span>
            potential network value
          </span>
        </div>
      </div>

      <div className="stats-grid three">
        <StatCard
          icon={Users}
          label="Businesses connected"
          value={businesses}
          note="in the demo network"
        />

        <StatCard
          icon={TrendingUp}
          label="Accepted exchanges"
          value={acceptedRequests}
          note="completed workflow"
        />

        <StatCard
          icon={CircleDollarSign}
          label="Estimated value"
          value={`₹${potentialValue.toLocaleString(
            "en-IN"
          )}`}
          note="potential, not verified revenue"
        />
      </div>

      <div className="panel methodology reveal">
        <h3>
          How ScrapSync measures impact
        </h3>

        <div className="method-grid">
          <div>
            <b>01</b>

            <span>
              Material committed
            </span>

            <p>
              Counts quantities attached to
              accepted exchange requests.
            </p>
          </div>

          <div>
            <b>02</b>

            <span>
              Potential value
            </span>

            <p>
              Quantity × agreed/listed unit
              price.
            </p>
          </div>

          <div>
            <b>03</b>

            <span>
              Transparency
            </span>

            <p>
              MVP figures are estimates until
              physical transactions are verified.
            </p>
          </div>
        </div>
      </div>
    </Shell>
  );
}


// ============================================================
// APP ROUTER
// ============================================================

function App() {
  return (
    <Routes>
      <Route
        path="/"
        element={<Overview />}
      />

      <Route
        path="/listings/new"
        element={<CreateListing />}
      />

      <Route
        path="/radar"
        element={<Radar />}
      />

      <Route
        path="/requests"
        element={<Requests />}
      />

      <Route
        path="/impact"
        element={<Impact />}
      />
    </Routes>
  );
}

export default App;