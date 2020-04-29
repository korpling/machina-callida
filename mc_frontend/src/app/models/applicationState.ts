import {TextData} from './textData';
import {ExerciseMC} from './exerciseMC';

export class ApplicationState {
    public currentSetup: TextData;
    public exerciseList: ExerciseMC[];
    public mostRecentSetup: TextData;

    constructor(init?: Partial<ApplicationState>) {
        Object.assign(this, init);
    }
}
