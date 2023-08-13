
import './App.css';
import { Routes, Route } from 'react-router-dom'

import PageLayout from './Views/PageLayout/PageLayout.tsx';
import CheckList from './Views/CheckListView/CheckList.tsx';
import NotFound from './Views/NotFoundView/NotFound.tsx';
import CheckView from './Views/CheckView/CheckView.tsx';
import RunView from './Views/RunView/RunView.tsx';
import StatusView from './Views/StatusView/Status.tsx';

function App() {
  return (
    <div className="App">
      <Routes>
        <Route path="/" element={<PageLayout />}>
          <Route index element={<CheckList />} />
          <Route path="status" element={<StatusView />} />
          <Route path="checks" element={<CheckList />} />
          <Route path="checks/:checkName/environments/:environmentName" element={<CheckView />} />
          <Route path="checks/:checkName/environments/:environmentName/runs/:runTimestamp" element={<RunView />} />
          <Route path="*" element={<NotFound />} />
        </Route>
      </Routes>
    </div>
  );
}

export default App;
