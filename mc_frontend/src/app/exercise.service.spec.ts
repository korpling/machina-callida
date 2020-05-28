import {TestBed} from '@angular/core/testing';

import {ExerciseService} from './exercise.service';
import {APP_BASE_HREF} from '@angular/common';
import {HttpClientTestingModule} from '@angular/common/http/testing';
import {IonicStorageModule} from '@ionic/storage';
import {TranslateTestingModule} from './translate-testing/translate-testing.module';

describe('ExerciseService', () => {
    let exerciseService: ExerciseService;
    beforeEach(() => {
        TestBed.configureTestingModule({
            imports: [
                HttpClientTestingModule,
                IonicStorageModule.forRoot(),
                TranslateTestingModule,
            ],
            providers: [
                {provide: APP_BASE_HREF, useValue: '/'},
            ],
        });
        exerciseService = TestBed.inject(ExerciseService);
    });

    it('should be created', () => {
        expect(exerciseService).toBeTruthy();
    });

    it('should create a GUID', () => {
        const guid: string = exerciseService.createGuid();
        expect(guid.length).toBe(36);
    });

    it('should initialize H5P', (done) => {
        let h5pCalled = false;
        const h5p = {
            jQuery: () => {
                h5pCalled = true;
                return {
                    empty: () => {
                        return {
                            h5p: (selector: string) => {
                            }
                        };
                    }
                };
            }, off: () => {
            }
        };
        spyOn(exerciseService.helperService, 'getH5P').and.returnValue(h5p);
        exerciseService.initH5P('').then(() => {
            expect(h5pCalled).toBe(true);
            done();
        });
    });
});
