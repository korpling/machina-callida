/* tslint:disable:variable-name */
import {Solution} from 'src/app/models/solution';

export class ExerciseMC {
    public conll: string;
    public correct_feedback: string;
    public eid: string;
    public exercise_type: string;
    public exercise_type_translation: string;
    public general_feedback: string;
    public incorrect_feedback: string;
    public instructions: string;
    public last_access_time: number;
    public matching_degree: number;
    public partially_correct_feedback: string;
    public search_values: string[];
    public solutions: Solution[];
    public text_complexity: number;
    public uri: string;
    public work_author: string;
    public work_title: string;

    constructor(init?: Partial<ExerciseMC>) {
        Object.assign(this, init);
    }
}

