import Activity from './Activity';

class ContextActivities {
  parent?: Activity[];
  grouping?: Activity[];
  category?: Activity[];
  other?: Activity[];

  constructor(init?: Partial<ContextActivities>) {
    Object.assign(this, init);
  }
}

export default ContextActivities;
