import Extensions from './Extensions';
import Score from 'src/app/models/xAPI/Score';

class Result {
    duration?: string;
    extensions?: Extensions;
    response?: string;
    score?: Score;

    constructor(init?: Partial<Result>) {
        Object.assign(this, init);
    }
}

export default Result;
