import StatementBase from './StatementBase';
import Actor from './Actor';

interface Statement extends StatementBase {
  id: string;
  authority: Actor;
  stored: string;
  timestamp: string;
  version: string;
}

export default Statement;
