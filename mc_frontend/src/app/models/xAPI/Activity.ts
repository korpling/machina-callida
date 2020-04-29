import Definition from './Definition';

class Activity {
    objectType: 'Activity';
    id: string;
    definition?: Definition;

    constructor(init?: Partial<Activity>) {
        Object.assign(this, init);
    }
}

export default Activity;
