/* tslint:disable:no-string-literal */
import {Component, OnInit} from '@angular/core';
import {ActivatedRoute} from '@angular/router';
import {ExerciseService} from 'src/app/exercise.service';
import {ExerciseParams} from '../models/exerciseParams';
import {CorpusService} from '../corpus.service';
import {HelperService} from '../helper.service';

@Component({
    selector: 'app-exercise',
    templateUrl: './exercise.page.html',
    styleUrls: ['./exercise.page.scss'],
})
export class ExercisePage implements OnInit {

    constructor(public activatedRoute: ActivatedRoute,
                public exerciseService: ExerciseService,
                public corpusService: CorpusService,
                public helperService: HelperService) {
    }

    initExercise(): Promise<void> {
        return new Promise<void>((resolve, reject) => {
            this.activatedRoute.queryParams.subscribe((params: ExerciseParams) => {
                this.exerciseService.loadExercise(params).then(() => {
                    return resolve();
                }, () => {
                    return reject();
                });
            });
        });
    }

    ngOnInit(): Promise<void> {
        return new Promise<void>((resolve) => {
            this.corpusService.checkAnnisResponse().then(() => {
                this.initExercise().then(() => {
                    return resolve();
                }, () => {
                    return resolve();
                });
            }, () => {
                return resolve();
            });
        });
    }

}
