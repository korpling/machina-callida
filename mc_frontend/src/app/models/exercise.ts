import {ExerciseType} from 'src/app/models/enum';
import {QueryMC} from 'src/app/models/queryMC';
import {Feedback} from 'src/app/models/feedback';

export class Exercise {
    public type: ExerciseType;
    public typeTranslation: string;
    public queryItems: QueryMC[];
    public feedback: Feedback;
    public instructionsTranslation: string;

    constructor(init?: Partial<Exercise>) {
        Object.assign(this, init);
    }
}

