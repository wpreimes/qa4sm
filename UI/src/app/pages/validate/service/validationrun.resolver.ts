import {Injectable} from '@angular/core';
import {ActivatedRouteSnapshot, Resolve, RouterStateSnapshot} from '@angular/router';
import {Observable} from 'rxjs';
import {ValidationrunService} from '../../../modules/core/services/validation-run/validationrun.service';
import {ValidationrunDto} from '../../../modules/core/services/validation-run/validationrun.dto';

@Injectable({
  providedIn: 'root'
})
export class ValidationrunResolver implements Resolve<ValidationrunDto> {
  constructor(private validationService: ValidationrunService) {
  }
  resolve(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<ValidationrunDto> {
    return this.validationService.getValidationRunById(route.paramMap.get('validationId'));
  }
}
