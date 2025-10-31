import React from 'react';
import { NavLink } from 'react-router-dom';

function Sidebar() {
  return (
    <div className="sidebar">
      <div className="sidebar__logo" title="YouDash">
        <img src="/images/favicon.ico" alt="Logo" />
      </div>

      <NavLink
        to="/map"
        className={({ isActive }) => `sidebar__icon ${isActive ? 'sidebar__active' : ''}`}
        title="Mapa"
      >
        <img src="/images/map.png" alt="Map" />
      </NavLink>

      <NavLink
        to="/explorer"
        className={({ isActive }) => `sidebar__icon ${isActive ? 'sidebar__active' : ''}`}
        title="Eksplorator"
      >
        <img src="/images/database.png" alt="Database" />
      </NavLink>

      <NavLink
        to="/log"
        className={({ isActive }) => `sidebar__icon ${isActive ? 'sidebar__active' : ''}`}
        title="Dziennik"
      >
        <img src="/images/log.png" alt="Log" />
      </NavLink>

      <NavLink
        to="/newdetectors"
        className={({ isActive }) => `sidebar__icon ${isActive ? 'sidebar__active' : ''}`}
        title="Nowe detektory"
      >
        <img src="/images/checklist.png" alt="Checklist" />
      </NavLink>

      <NavLink
        to="/tickets"
        className={({ isActive }) => `sidebar__icon sidebar__icon--hidden ${isActive ? 'sidebar__active' : ''}`}
        title="Zgłoszenia"
      >
        <img src="/images/tickets.png" alt="Tickets" />
      </NavLink>

      <NavLink
        to="/hardware"
        className={({ isActive }) => `sidebar__icon sidebar__icon--hidden ${isActive ? 'sidebar__active' : ''}`}
        title="Sprzęt"
      >
        <img src="/images/hardware.png" alt="Hardware" />
      </NavLink>

      <NavLink
        to="/contracts"
        className={({ isActive }) => `sidebar__icon sidebar__icon--hidden ${isActive ? 'sidebar__active' : ''}`}
        title="Umowy"
      >
        <img src="/images/contracts.png" alt="Contracts" />
      </NavLink>
    </div>
  );
}

export default Sidebar;
